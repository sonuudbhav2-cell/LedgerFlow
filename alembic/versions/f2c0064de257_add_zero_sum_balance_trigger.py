"""add_zero_sum_balance_trigger

Revision ID: f2c0064de257
Revises: 67a7b755039d
Create Date: 2026-08-29 16:41:58.153564

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f2c0064de257'
down_revision = '67a7b755039d'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create function to check debit/credit balance equality per journal entry
    op.execute("""
    CREATE OR REPLACE FUNCTION check_journal_entry_balance()
    RETURNS TRIGGER AS $$
    DECLARE
        v_debit_sum NUMERIC(20, 4);
        v_credit_sum NUMERIC(20, 4);
        v_entry_id UUID;
    BEGIN
        v_entry_id := COALESCE(NEW.journal_entry_id, OLD.journal_entry_id);

        SELECT 
            COALESCE(SUM(CASE WHEN direction = 'DEBIT' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN direction = 'CREDIT' THEN amount ELSE 0 END), 0)
        INTO v_debit_sum, v_credit_sum
        FROM postings
        WHERE journal_entry_id = v_entry_id;

        IF v_debit_sum <> v_credit_sum THEN
            RAISE EXCEPTION 'Double-entry violation: Total DEBIT (%) does not equal total CREDIT (%) for journal entry %',
                v_debit_sum, v_credit_sum, v_entry_id;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 2. Create constraint trigger deferred until transaction COMMIT
    op.execute("""
    CREATE CONSTRAINT TRIGGER trigger_check_journal_entry_balance
    AFTER INSERT OR UPDATE OR DELETE ON postings
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW
    EXECUTE FUNCTION check_journal_entry_balance();
    """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trigger_check_journal_entry_balance ON postings;")
    op.execute("DROP FUNCTION IF EXISTS check_journal_entry_balance();")