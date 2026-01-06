from app.infrastructure.db.models.audit_log import AuditLog

async def write_audit(session, *, actor, action, entity, entity_id, tenant_id=None):
    log = AuditLog(
        actor=actor,
        action=action,
        entity=entity,
        entity_id=str(entity_id),
        tenant_id=tenant_id
    )
    session.add(log)
    await session.commit()
