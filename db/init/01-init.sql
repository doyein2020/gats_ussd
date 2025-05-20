-- Création des extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Création des tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS ussd_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    service_code VARCHAR(20),
    current_menu VARCHAR(100),
    session_data JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS ussd_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    session_id INTEGER NOT NULL REFERENCES ussd_sessions(id),
    input_text VARCHAR(255),
    response_text TEXT,
    menu_level VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    response_time_ms INTEGER,
    is_error BOOLEAN DEFAULT FALSE,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS ussd_services (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    menu_structure JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS service_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    service_id INTEGER NOT NULL REFERENCES ussd_services(id),
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS survey_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    survey_id VARCHAR(50) NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    response_value VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Création des index
CREATE INDEX idx_users_phone_number ON users(phone_number);
CREATE INDEX idx_ussd_sessions_session_id ON ussd_sessions(session_id);
CREATE INDEX idx_ussd_sessions_user_id ON ussd_sessions(user_id);
CREATE INDEX idx_ussd_sessions_is_active ON ussd_sessions(is_active);
CREATE INDEX idx_ussd_logs_user_id ON ussd_logs(user_id);
CREATE INDEX idx_ussd_logs_session_id ON ussd_logs(session_id);
CREATE INDEX idx_ussd_logs_created_at ON ussd_logs(created_at);
CREATE INDEX idx_ussd_services_code ON ussd_services(code);
CREATE INDEX idx_service_subscriptions_user_id ON service_subscriptions(user_id);
CREATE INDEX idx_service_subscriptions_service_id ON service_subscriptions(service_id);
CREATE INDEX idx_survey_responses_user_id ON survey_responses(user_id);
CREATE INDEX idx_survey_responses_survey_id ON survey_responses(survey_id);

-- Insertion de données initiales pour les services
INSERT INTO ussd_services (code, name, description, menu_structure)
VALUES 
('*123#', 'Service Principal', 'Service USSD principal de l''entreprise', 
'{
    "main": {
        "title": "Menu Principal",
        "options": [
            {"code": "1", "text": "Consultation de solde", "next": "balance"},
            {"code": "2", "text": "S''inscrire aux services", "next": "services"},
            {"code": "3", "text": "Suivi de commande", "next": "order_tracking"},
            {"code": "4", "text": "Sondages", "next": "survey"}
        ]
    },
    "services": {
        "title": "Services disponibles",
        "options": [
            {"code": "1", "text": "Service A", "next": "service_a"},
            {"code": "2", "text": "Service B", "next": "service_b"},
            {"code": "3", "text": "Service C", "next": "service_c"}
        ]
    }
}'::jsonb),

('SRV-A', 'Service A', 'Description du Service A', 
'{
    "main": {
        "title": "Service A",
        "options": [
            {"code": "1", "text": "Activer", "next": "activate"},
            {"code": "2", "text": "Désactiver", "next": "deactivate"},
            {"code": "3", "text": "Informations", "next": "info"}
        ]
    }
}'::jsonb),

('SRV-B', 'Service B', 'Description du Service B', 
'{
    "main": {
        "title": "Service B",
        "options": [
            {"code": "1", "text": "Activer", "next": "activate"},
            {"code": "2", "text": "Désactiver", "next": "deactivate"},
            {"code": "3", "text": "Informations", "next": "info"}
        ]
    }
}'::jsonb),

('SRV-C', 'Service C', 'Description du Service C', 
'{
    "main": {
        "title": "Service C",
        "options": [
            {"code": "1", "text": "Activer", "next": "activate"},
            {"code": "2", "text": "Désactiver", "next": "deactivate"},
            {"code": "3", "text": "Informations", "next": "info"}
        ]
    }
}'::jsonb);

-- Création d'un utilisateur de test
INSERT INTO users (phone_number, first_name, last_name)
VALUES ('+123456789', 'Utilisateur', 'Test');

-- Création de vues pour faciliter les rapports
CREATE OR REPLACE VIEW vw_active_sessions AS
SELECT 
    s.id,
    s.session_id,
    u.phone_number,
    u.first_name,
    u.last_name,
    s.current_menu,
    s.started_at,
    s.last_activity,
    EXTRACT(EPOCH FROM (NOW() - s.last_activity)) AS seconds_since_last_activity
FROM 
    ussd_sessions s
JOIN 
    users u ON s.user_id = u.id
WHERE 
    s.is_active = TRUE;

CREATE OR REPLACE VIEW vw_user_activity AS
SELECT 
    u.id,
    u.phone_number,
    u.first_name,
    u.last_name,
    COUNT(DISTINCT s.id) AS total_sessions,
    COUNT(l.id) AS total_interactions,
    MAX(s.last_activity) AS last_activity,
    SUM(CASE WHEN l.is_error = TRUE THEN 1 ELSE 0 END) AS error_count
FROM 
    users u
LEFT JOIN 
    ussd_sessions s ON u.id = s.user_id
LEFT JOIN 
    ussd_logs l ON s.id = l.session_id
GROUP BY 
    u.id, u.phone_number, u.first_name, u.last_name;

-- Fonctions utilitaires
CREATE OR REPLACE FUNCTION end_inactive_sessions(timeout_minutes INTEGER)
RETURNS INTEGER AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    UPDATE ussd_sessions
    SET 
        is_active = FALSE,
        ended_at = NOW()
    WHERE 
        is_active = TRUE 
        AND last_activity < NOW() - (timeout_minutes * INTERVAL '1 minute');
    
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RETURN affected_rows;
END;
$$ LANGUAGE plpgsql;
