
-- ============================================================
-- Warband HQ - MySQL database schema
-- ============================================================

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    blizzard_account_id VARCHAR(24) NOT NULL,
    role VARCHAR(8) NOT NULL DEFAULT 'USER',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,

    PRIMARY KEY (id),
    CONSTRAINT uq_users_blizzard_account_id
        UNIQUE (blizzard_account_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- 2. Characters
CREATE TABLE IF NOT EXISTS characters (
    id INT NOT NULL AUTO_INCREMENT,
    blizzard_character_id INT NOT NULL,
    user_id INT NOT NULL,
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_synced_at DATETIME NULL,

    PRIMARY KEY (id),
    CONSTRAINT uq_character_user_blizzard_id
        UNIQUE (user_id, blizzard_character_id),

    INDEX ix_characters_user_id (user_id),

    CONSTRAINT fk_characters_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- 3. Authentication sessions
CREATE TABLE IF NOT EXISTS authentication_sessions (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    access_token TEXT NOT NULL,
    session_token VARCHAR(128) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT uq_authentication_sessions_session_token
        UNIQUE (session_token),

    INDEX ix_authentication_sessions_user_id (user_id),

    CONSTRAINT fk_authentication_sessions_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- 4. Global tags catalogue
CREATE TABLE IF NOT EXISTS tags (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(24) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT uq_tags_name
        UNIQUE (name)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- 5. Character-tag associations
CREATE TABLE IF NOT EXISTS character_tags (
    character_id INT NOT NULL,
    tag_id INT NOT NULL,

    PRIMARY KEY (character_id, tag_id),
    INDEX ix_character_tags_tag_id (tag_id),

    CONSTRAINT fk_character_tags_character
        FOREIGN KEY (character_id)
        REFERENCES characters (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_character_tags_tag
        FOREIGN KEY (tag_id)
        REFERENCES tags (id)
        ON DELETE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- 6. Personal goals
CREATE TABLE IF NOT EXISTS goals (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    character_id INT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    INDEX ix_goals_user_id (user_id),
    INDEX ix_goals_character_id (character_id),

    CONSTRAINT ck_goals_status
        CHECK (
            status IN (
                'IN_PROGRESS',
                'ON_HOLD',
                'COMPLETED',
                'ABANDONED'
            )
        ),

    CONSTRAINT fk_goals_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_goals_character
        FOREIGN KEY (character_id)
        REFERENCES characters (id)
        ON DELETE SET NULL
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
