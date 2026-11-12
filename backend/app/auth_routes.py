"""Account endpoints. Tokens are only returned in HttpOnly session cookies."""
import hashlib
import re
import sqlite3
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool

from app.auth import COOKIE_NAME, SESSION_SECONDS, hash_password, verify_password
from app.config import settings
from app.persistence import capture_state
from app.sessions import LearnerSession

router = APIRouter(prefix='/api/auth', tags=['Comptes'])


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator('email')
    @classmethod
    def email_format(cls, value):
        value = value.strip().casefold()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
            raise ValueError('Adresse e-mail invalide.')
        return value


class Registration(Credentials):
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=15, max_length=128)

    @field_validator('name')
    @classmethod
    def name_not_blank(cls, value):
        if not value.strip():
            raise ValueError('Un prénom est requis.')
        return value.strip()


def store_for(request):
    store = request.app.state.auth
    if store is None:
        raise HTTPException(503, 'Les comptes sont désactivés sur cette installation.')
    return store


def public_session(store, token):
    user = store.authenticate(token)
    return {'authentication_required': True, 'user': {
        'id': user['user_id'], 'email': user['email'], 'name': user['name'],
    }, 'learner_id': user['learner_id']}


def set_cookie(response, token):
    response.set_cookie(COOKIE_NAME, token, max_age=SESSION_SECONDS,
                        httponly=True, secure=settings.auth_cookie_secure, samesite='strict', path='/')


def throttle(request, store, action, email):
    ip = request.client.host if request.client else 'unknown'
    buckets = [(action + ':ip:' + hashlib.sha256(ip.encode()).hexdigest(), 30 if action == 'login' else 10),
               (action + ':mail:' + hashlib.sha256(email.encode()).hexdigest(), 10 if action == 'login' else 5)]
    if not store.throttle(buckets):
        raise HTTPException(429, 'Trop de tentatives. Réessayez dans 15 minutes.', headers={'Retry-After': '900'})


@router.get('/session')
async def session(request: Request):
    if not settings.auth_enabled:
        return {'authentication_required': False, 'user': None, 'learner_id': None}
    store = store_for(request)
    token = request.cookies.get(COOKIE_NAME)
    if not store.authenticate(token):
        raise HTTPException(401, 'Connectez-vous pour accéder à votre compte.')
    return public_session(store, token)


@router.post('/register', status_code=201)
async def register(data: Registration, request: Request, response: Response):
    store = store_for(request)
    throttle(request, store, 'register', data.email)
    async with request.app.state.password_workers:
        digest = await run_in_threadpool(hash_password, data.password)
    learner = LearnerSession(learner_id=str(uuid4()))
    learner.agent.learner.set_name(data.name)
    try:
        token = store.create_account(data.email, digest, data.name, learner.learner_id,
                                     capture_state(learner.agent, learner.assessment))
    except sqlite3.IntegrityError:
        raise HTTPException(409, 'Impossible de créer ce compte. Essayez de vous connecter.') from None
    request.app.state.learners.sessions[learner.learner_id] = learner
    set_cookie(response, token)
    return public_session(store, token)


@router.post('/login')
async def login(data: Credentials, request: Request, response: Response):
    store = store_for(request)
    throttle(request, store, 'login', data.email)
    account = store.credentials(data.email)
    async with request.app.state.password_workers:
        valid = await run_in_threadpool(verify_password, data.password,
                                         account['password_hash'] if account else store.dummy_password)
    if not valid or account is None:
        raise HTTPException(401, 'Adresse e-mail ou mot de passe incorrect.')
    token = store.new_session(account['user_id'], request.cookies.get(COOKIE_NAME))
    set_cookie(response, token)
    return public_session(store, token)


@router.post('/logout')
async def logout(request: Request, response: Response):
    store_for(request).logout(request.cookies.get(COOKIE_NAME))
    response.delete_cookie(COOKIE_NAME, path='/', secure=settings.auth_cookie_secure,
                           httponly=True, samesite='strict')
    return {'status': 'signed_out'}
