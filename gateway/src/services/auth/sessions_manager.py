import uuid
from collections.abc import Mapping
from types import SimpleNamespace
from typing import Any

from eyemath_schemas import Session# type: ignore[import-untyped]

from loguru import logger

from src.core.utils import EnvTools, StringTools, TimeTools, ValidatingTools
from src.services.valkey.valkey import ValkeyService


class SessionsManager:
    def __init__(self) -> None:
        self.session_max_life_days: int = int(EnvTools.required_load_env_var("SESSIONS_MAX_LIFE_DAYS"))
        self.session_inactive_days: int = int(EnvTools.required_load_env_var("SESSIONS_INACTIVE_DAYS"))
        self.valkey_service: Any = ValkeyService()


    def _days_to_seconds(self, days: int) -> int:
        return days * 24 * 60 * 60


    def _clamped_ttl_seconds(self, now_ts: int, mtl_ts: int) -> int:
        """
        Returns TTL = min(inactive_window, mtl - now), not < 0.
        """
        remaining = max(0, mtl_ts - now_ts)
        return min(remaining, self._days_to_seconds(self.session_inactive_days))


    def create_session(self, user_id: str, *,
        user_agent: str, client_id: str,
        local_system_time_zone: str, platform: str, ip: str,
    ) -> dict[str, str]:

        sid = uuid.uuid4()
        key = f"Session:{sid}"

        now_time_stamp = TimeTools.now_time_stamp()
        mtl_time_stamp = now_time_stamp + self._days_to_seconds(self.session_max_life_days)

        dsh: str = StringTools.hash_string(
            f"{user_agent}{client_id}{local_system_time_zone}{platform}"
        )

        ish: str = StringTools.hash_string(ip)

        model = Session(
            sub=user_id,
            iat=now_time_stamp,
            mtl=mtl_time_stamp,
            dsh=dsh,
            ish=ish,
        )

        self.valkey_service.valkey.hset(key, mapping={k: str(v) for k, v in model.model_dump().items()})

        ttl = self._clamped_ttl_seconds(now_time_stamp, mtl_time_stamp)
        if ttl > 0:
            self.valkey_service.valkey.expire(key, ttl)
        else:
            self.valkey_service.valkey.delete(key)

        logger.debug(f"Created new session: {str(sid)} for user: {user_id}")

        return {
            "session_id": str(sid),
            "iat": str(now_time_stamp),
            "mtl": str(mtl_time_stamp),
        }


    def touch_session(self, session_id: str) -> bool:
        sess = self.get_session(session_id)

        if not sess:
            return False

        now_ts = TimeTools.now_time_stamp()
        ttl = self._clamped_ttl_seconds(now_ts, sess.mtl)

        if ttl <= 0:
            self.valkey_service.valkey.delete(f"Session:{session_id}")
            return False

        self.valkey_service.valkey.expire(f"Session:{session_id}", ttl)
        logger.debug(f"Touched session: {session_id}")
        return True


    def delete_session(self, session_id: str) -> None:
        session_key = f"Session:{session_id}"
        self.valkey_service.valkey.delete(session_key)

    
    def delete_all_sessions_for_user(self, user_id: str) -> int:
        """
        Deletes all sessions (Session keys:{sid}) belonging to the user user_id.
        Returns the amount of deleted sessions.
        """
        uid: str = user_id
        deleted_total: int = 0
        cursor: int = 0
        pattern: str = "Session:*"

        while True:
            cursor, keys = self.valkey_service.valkey.scan(cursor=cursor, match=pattern, count=1000)

            if keys:
                pipe = self.valkey_service.valkey.pipeline()
                for k in keys:
                    pipe.hget(k, "sub")
                subs = pipe.execute()

                to_delete = [k for k, s in zip(keys, subs, strict=False) if s == uid]

                if to_delete:
                    pipe_del = self.valkey_service.valkey.pipeline()
                    for k in to_delete:
                        pipe_del.delete(k)
                    results = pipe_del.execute()
                    deleted_total += sum(1 for r in results if r)

            if cursor == 0:
                break

        if deleted_total:
            logger.debug(f"Deleted {deleted_total} sessions for user: {uid}")
        return deleted_total


    def is_session_exists(self, session_id: str) -> bool:
         return self.get_session(session_id) is not None


    def get_session(self, session_id: str) -> Session | None:
        session_key = f"Session:{session_id}"
        data = self.valkey_service.valkey.hgetall(session_key)
        if not data:
            return None
        try:
            dto_session = self.validate_session(data)
            if isinstance(dto_session, list):
                return dto_session[0] if dto_session else None
            return dto_session
            
        except Exception as ex:
            logger.warning(f"Session {session_id} failed validation: {ex}")
            return None


    def validate_session(self, raw: Any) -> Session | None:
        if raw is None:
            return None
        obj = SimpleNamespace(**raw) if isinstance(raw, Mapping) else raw
        dto = ValidatingTools.validate_models_by_schema(obj, Session)
        return dto if not isinstance(dto, list) else (dto[0] if dto else None)


    def get_test_dsh(self) -> dict[str, str]:
        return {
            "user_agent": "bla_bla",
            "client_id": "bla_bla",
            "local_system_time_zone": "bla_bla",
            "platform": "bla_bla",
        }


    def get_test_client_ip(self) -> str:
       return "192.168.0.1"
        

        
