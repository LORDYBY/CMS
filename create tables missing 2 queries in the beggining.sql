CREATE TYPE device_state AS ENUM (
  'PENDING',
  'APPROVED',
  'ACTIVE',
  'DISABLED',
  'REVOKED'
);

CREATE TYPE content_state AS ENUM (
  'DRAFT',
  'PENDING_APPROVAL',
  'APPROVED',
  'PUBLISHED',
  'ARCHIVED'
);

CREATE TYPE audit_action AS ENUM (
  'CREATE',
  'UPDATE',
  'DELETE',
  'APPROVE',
  'REVOKE',
  'LOGIN',
  'EMERGENCY'
);



CREATE TABLE tenants (
  id              UUID PRIMARY KEY,
  name            TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at      TIMESTAMPTZ
);
CREATE TABLE users (
  id              UUID PRIMARY KEY,
  tenant_id       UUID NOT NULL REFERENCES tenants(id),
  email           TEXT NOT NULL,
  password_hash   TEXT NOT NULL,
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at      TIMESTAMPTZ,
  UNIQUE (tenant_id, email)
);
CREATE TABLE roles (
  id          UUID PRIMARY KEY,
  tenant_id   UUID NOT NULL REFERENCES tenants(id),
  name        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, name)
);
CREATE TABLE user_roles (
  user_id UUID NOT NULL REFERENCES users(id),
  role_id UUID NOT NULL REFERENCES roles(id),
  PRIMARY KEY (user_id, role_id)
);
CREATE TABLE audit_logs (
  id            BIGSERIAL PRIMARY KEY,
  tenant_id     UUID NOT NULL REFERENCES tenants(id),
  actor_user_id UUID,
  actor_device_id UUID,
  action        audit_action NOT NULL,
  entity_type   TEXT NOT NULL,
  entity_id     UUID,
  payload       JSONB NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_tenant_time ON audit_logs (tenant_id, created_at DESC);
CREATE TABLE devices (
  id                UUID PRIMARY KEY,
  tenant_id         UUID REFERENCES tenants(id),
  fingerprint       TEXT NOT NULL UNIQUE,
  name              TEXT,
  state             device_state NOT NULL DEFAULT 'PENDING',
  token_hash        TEXT,
  approved_at       TIMESTAMPTZ,
  revoked_at        TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at      TIMESTAMPTZ
);

CREATE TABLE screens (
  id          UUID PRIMARY KEY,
  tenant_id   UUID NOT NULL REFERENCES tenants(id),
  device_id   UUID NOT NULL REFERENCES devices(id),
  name        TEXT NOT NULL,
  resolution  TEXT NOT NULL,
  orientation TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE screen_layouts (
  id          UUID PRIMARY KEY,
  tenant_id   UUID NOT NULL REFERENCES tenants(id),
  name        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE screen_zones (
  id            UUID PRIMARY KEY,
  tenant_id     UUID NOT NULL REFERENCES tenants(id),
  layout_id     UUID NOT NULL REFERENCES screen_layouts(id),
  name          TEXT NOT NULL,
  x             INTEGER NOT NULL,
  y             INTEGER NOT NULL,
  width         INTEGER NOT NULL,
  height        INTEGER NOT NULL
);
CREATE TABLE media_assets (
  id            UUID PRIMARY KEY,
  tenant_id     UUID NOT NULL REFERENCES tenants(id),
  filename      TEXT NOT NULL,
  mime_type     TEXT NOT NULL,
  size_bytes    BIGINT NOT NULL,
  checksum      TEXT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE content_versions (
  id              UUID PRIMARY KEY,
  tenant_id       UUID NOT NULL REFERENCES tenants(id),
  media_asset_id  UUID NOT NULL REFERENCES media_assets(id),
  version_number  INTEGER NOT NULL,
  state           content_state NOT NULL DEFAULT 'DRAFT',
  created_by      UUID NOT NULL REFERENCES users(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_at     TIMESTAMPTZ,
  UNIQUE (media_asset_id, version_number)
);

CREATE TABLE playlists (
  id          UUID PRIMARY KEY,
  tenant_id   UUID NOT NULL REFERENCES tenants(id),
  name        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE playlist_items (
  id                 UUID PRIMARY KEY,
  tenant_id          UUID NOT NULL REFERENCES tenants(id),
  playlist_id        UUID NOT NULL REFERENCES playlists(id),
  content_version_id UUID NOT NULL REFERENCES content_versions(id),
  position           INTEGER NOT NULL,
  duration_seconds   INTEGER
);
CREATE TABLE schedules (
  id            UUID PRIMARY KEY,
  tenant_id     UUID NOT NULL REFERENCES tenants(id),
  zone_id       UUID NOT NULL REFERENCES screen_zones(id),
  playlist_id   UUID NOT NULL REFERENCES playlists(id),
  start_time    TIMESTAMPTZ NOT NULL,
  end_time      TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE emergency_messages (
  id            UUID PRIMARY KEY,
  tenant_id     UUID NOT NULL REFERENCES tenants(id),
  title         TEXT NOT NULL,
  message       TEXT,
  severity      TEXT NOT NULL,
  starts_at     TIMESTAMPTZ NOT NULL,
  ends_at       TIMESTAMPTZ NOT NULL,
  created_by    UUID NOT NULL REFERENCES users(id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE emergency_media (
  id                    UUID PRIMARY KEY,
  tenant_id             UUID NOT NULL REFERENCES tenants(id),
  emergency_message_id  UUID NOT NULL REFERENCES emergency_messages(id),
  media_asset_id        UUID NOT NULL REFERENCES media_assets(id)
);
CREATE TABLE device_heartbeats (
  id          BIGSERIAL PRIMARY KEY,
  tenant_id   UUID NOT NULL REFERENCES tenants(id),
  device_id   UUID NOT NULL REFERENCES devices(id),
  heartbeat_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_heartbeat_device_time 
ON device_heartbeats (device_id, heartbeat_at DESC);


CREATE TABLE locations (
  id          UUID PRIMARY KEY,
  tenant_id   UUID NOT NULL REFERENCES tenants(id),
  parent_id   UUID REFERENCES locations(id),
  name        TEXT NOT NULL
);
