# Инициализация БД и тестовые данные (Seed)

Для соответствия требованиям ТЗ по заполнению таблиц тестовыми данными, выполните этот SQL-скрипт в вашей БД `task_db` после применения миграций Alembic (`alembic upgrade head`).

В данном примере создаются:
1. **Роли**: ADMIN, USER, BUSINESS.
2. **Ресурсы**: USERS, GOODS, RULES, ORDERS.
3. **Правила (Access Rules)**, связывающие роли и ресурсы.

```sql
-- 1. Создание ролей (Фиксированные UUID для удобства)
INSERT INTO roles (id, name) VALUES 
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'ADMIN'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'USER'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'BUSINESS')
ON CONFLICT (name) DO NOTHING;

-- 2. Создание ресурсов (Фиксированные UUID для удобства)
INSERT INTO resources (id, name) VALUES 
('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', 'USERS'),
('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'GOODS'),
('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33', 'RULES'),
('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380c44', 'ORDERS')
ON CONFLICT (name) DO NOTHING;

-- 2.5 Создание базового администратора (admin@admin.com / admin123)
-- Пароль захеширован с помощью bcrypt (admin123)
INSERT INTO users (id, email, password_hash, first_name, last_name, surname, role_id, "isActive") VALUES
('11111111-1111-1111-1111-111111111111', 'admin@admin.com', '$2b$12$KQQP3pX.0gV.oMzVpXn1/OuGz9/O8k605l2r2Tf564S3a2H.W45Ea', 'Admin', 'Root', 'System', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', true)
ON CONFLICT (email) DO NOTHING;

-- 3. Базовые правила доступа (Access Roles Rules)

-- Очистка старых правил перед заливкой новых (опционально)
TRUNCATE TABLE access_roles_rules CASCADE;

-- ==================== ПРАВИЛА ДЛЯ АДМИНА (ADMIN) ==================== --
-- Может всё везде (кроме самостоятельного создания заказов)
INSERT INTO access_roles_rules (id, role_id, resource_id, read_p, read_all_p, create_p, update_p, update_all_p, delete_p, delete_all_p)
VALUES 
(gen_random_uuid(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', true, true, true, true, true, true, true), -- USERS
(gen_random_uuid(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', true, true, true, true, true, true, true), -- GOODS
(gen_random_uuid(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33', true, true, true, true, true, true, true), -- RULES (только админы читают и меняют)
(gen_random_uuid(), 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380c44', true, true, false, false, false, false, false); -- ORDERS

-- ==================== ПРАВИЛА ДЛЯ ЮЗЕРА (USER) ==================== --
INSERT INTO access_roles_rules (id, role_id, resource_id, read_p, read_all_p, create_p, update_p, update_all_p, delete_p, delete_all_p)
VALUES 
(gen_random_uuid(), 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', true, false, false, true, false, true, false), -- USERS (читает и правит себя)
(gen_random_uuid(), 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', true, true, false, false, false, false, false), -- GOODS (только просмотр)
(gen_random_uuid(), 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380c44', true, false, true, false, false, false, false); -- ORDERS (читает свои заказы, создаёт заказы)

-- ==================== ПРАВИЛА ДЛЯ БИЗНЕСА (BUSINESS) ==================== --
INSERT INTO access_roles_rules (id, role_id, resource_id, read_p, read_all_p, create_p, update_p, update_all_p, delete_p, delete_all_p)
VALUES 
(gen_random_uuid(), 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', true, true, true, true, false, true, false); -- GOODS (создаёт товары, правит и удаляет свои)
```
