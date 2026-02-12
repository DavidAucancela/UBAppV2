-- Después de restaurar backup_utf8.sql, ejecutar este script para que Django encuentre las tablas.
-- El backup local usaba tipo_contenido y logs; Django espera django_content_type y django_admin_log.

ALTER TABLE IF EXISTS public.tipo_contenido RENAME TO django_content_type;
ALTER TABLE IF EXISTS public.logs RENAME TO django_admin_log;
