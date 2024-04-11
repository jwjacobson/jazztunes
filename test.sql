BEGIN;
--
-- Remove field is_contrafact from tune
--
ALTER TABLE "tune_tune" DROP COLUMN "is_contrafact" CASCADE;
COMMIT;
