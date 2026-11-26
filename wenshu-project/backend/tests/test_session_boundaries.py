import asyncio
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app.api.routes.chat import _assert_session_owner
from app.storage.store import MemoryStore

@pytest.mark.asyncio
async def test_first_session_claim_cannot_be_overwritten():
    store = MemoryStore()
    container = SimpleNamespace(store=store)
    outcomes = await asyncio.gather(
        _assert_session_owner(container, 'fresh', 'alice'),
        _assert_session_owner(container, 'fresh', 'bob'), return_exceptions=True,
    )
    assert sum(isinstance(o, HTTPException) for o in outcomes) == 1
    assert (await store.get('session_owners', 'fresh'))['user_id'] == 'alice'

@pytest.mark.asyncio
async def test_deleted_session_cannot_be_claimed_again():
    store = MemoryStore()
    await store.upsert('session_owners', {'_id':'old','user_id':'alice','deleted':True})
    with pytest.raises(HTTPException):
        await _assert_session_owner(SimpleNamespace(store=store), 'old', 'alice')

@pytest.mark.asyncio
async def test_legacy_session_owner_is_preserved():
    store = MemoryStore()
    await store.upsert('traces', {'_id':'trace','session_id':'legacy','user_id':'alice'})
    with pytest.raises(HTTPException):
        await _assert_session_owner(SimpleNamespace(store=store), 'legacy', 'bob')
    await _assert_session_owner(SimpleNamespace(store=store), 'legacy', 'alice')
    assert (await store.get('session_owners','legacy'))['user_id'] == 'alice'
