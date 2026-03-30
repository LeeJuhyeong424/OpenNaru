"""초기 스키마 v1.2 19개 테이블

Revision ID: 6efd26028441
Revises:
Create Date: 2026-03-30 21:13:37.493606

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6efd26028441'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users (의존 없음)
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(40), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('oauth_provider', sa.String(30), nullable=True),
        sa.Column('oauth_id', sa.String(255), nullable=True),
        sa.Column('avatar_file_id', sa.BigInteger(), nullable=True),
        sa.Column('is_global_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )
    op.create_index('ix_users_uuid', 'users', ['uuid'], unique=True)

    # 2. wikis (의존 없음)
    op.create_table(
        'wikis',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(60), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_file_id', sa.BigInteger(), nullable=True),
        sa.Column('lang', sa.String(10), nullable=False, server_default='ko'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('default_edit_acl', sa.String(20), nullable=False, server_default='anonymous'),
        sa.Column('allow_anon_edit', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index('ix_wikis_uuid', 'wikis', ['uuid'], unique=True)

    # 3. wiki_members (→ wikis, users)
    op.create_table(
        'wiki_members',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='member'),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('blocked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('block_reason', sa.Text(), nullable=True),
        sa.Column('block_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wiki_id', 'user_id', name='uq_wiki_members_wiki_user'),
    )
    op.create_index('ix_wiki_members_wiki_id', 'wiki_members', ['wiki_id'], unique=False)
    op.create_index('ix_wiki_members_user_id', 'wiki_members', ['user_id'], unique=False)

    # 4. blocks (→ wikis, users)
    op.create_table(
        'blocks',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('blocked_by', sa.BigInteger(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['blocked_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_blocks_wiki_id', 'blocks', ['wiki_id'], unique=False)
    op.create_index('ix_blocks_user_id', 'blocks', ['user_id'], unique=False)

    # 5. files (→ wikis, users)
    op.create_table(
        'files',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('uploader_id', sa.BigInteger(), nullable=True),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('license', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['uploader_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_files_uuid', 'files', ['uuid'], unique=True)
    op.create_index('ix_files_wiki_id', 'files', ['wiki_id'], unique=False)

    # 6. pages (→ wikis) — latest_revision_id FK는 use_alter로 나중에 추가
    op.create_table(
        'pages',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('namespace', sa.String(30), nullable=False, server_default='main'),
        sa.Column('slug', sa.String(500), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('content_html', sa.Text(), nullable=False, server_default=''),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('latest_revision_id', sa.BigInteger(), nullable=True),
        sa.Column('redirect_to', sa.String(500), nullable=True),
        sa.Column('is_redirect', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('protection_level', sa.String(20), nullable=False, server_default='none'),
        sa.Column('view_count', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wiki_id', 'namespace', 'slug', name='uq_pages_wiki_ns_slug'),
    )
    op.create_index('ix_pages_uuid', 'pages', ['uuid'], unique=True)
    op.create_index('ix_pages_wiki_id', 'pages', ['wiki_id'], unique=False)

    # 7. page_revisions (→ pages, users, wikis)
    op.create_table(
        'page_revisions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('page_id', sa.BigInteger(), nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('editor_id', sa.BigInteger(), nullable=True),
        sa.Column('editor_ip', sa.String(45), nullable=True),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('comment', sa.String(500), nullable=True),
        sa.Column('is_minor', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_bot', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('byte_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('byte_diff', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_suppressed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id']),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['editor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_page_revisions_page_id', 'page_revisions', ['page_id'], unique=False)
    op.create_index('ix_page_revisions_wiki_id', 'page_revisions', ['wiki_id'], unique=False)

    # pages.latest_revision_id FK (순환 참조 — use_alter)
    op.create_foreign_key(
        'fk_pages_latest_revision',
        'pages', 'page_revisions',
        ['latest_revision_id'], ['id'],
        use_alter=True,
    )

    # 8. revision_suppressions (→ page_revisions, users)
    op.create_table(
        'revision_suppressions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('revision_id', sa.BigInteger(), nullable=False),
        sa.Column('suppressed_by', sa.BigInteger(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['revision_id'], ['page_revisions.id']),
        sa.ForeignKeyConstraint(['suppressed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_revision_suppressions_revision_id', 'revision_suppressions', ['revision_id'], unique=False)

    # 9. page_acls (→ pages, users)
    op.create_table(
        'page_acls',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('page_id', sa.BigInteger(), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('acl_value', sa.String(20), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('page_id', 'action', name='uq_page_acls_page_action'),
    )
    op.create_index('ix_page_acls_page_id', 'page_acls', ['page_id'], unique=False)

    # 10. namespace_acls (→ wikis)
    op.create_table(
        'namespace_acls',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('namespace', sa.String(30), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('acl_value', sa.String(20), nullable=False, server_default='anonymous'),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wiki_id', 'namespace', 'action', name='uq_namespace_acls_wiki_ns_action'),
    )
    op.create_index('ix_namespace_acls_wiki_id', 'namespace_acls', ['wiki_id'], unique=False)

    # 11. user_acl_overrides (→ wikis, users)
    op.create_table(
        'user_acl_overrides',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('override_type', sa.String(20), nullable=False),
        sa.Column('grade', sa.String(20), nullable=True),
        sa.Column('action', sa.String(20), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('granted_by', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_acl_overrides_wiki_id', 'user_acl_overrides', ['wiki_id'], unique=False)
    op.create_index('ix_user_acl_overrides_user_id', 'user_acl_overrides', ['user_id'], unique=False)

    # 12. categories (→ wikis, 자기참조)
    op.create_table(
        'categories',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('slug', sa.String(300), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wiki_id', 'slug', name='uq_categories_wiki_slug'),
    )
    op.create_index('ix_categories_wiki_id', 'categories', ['wiki_id'], unique=False)

    # 13. page_categories (→ pages, categories)
    op.create_table(
        'page_categories',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('page_id', sa.BigInteger(), nullable=False),
        sa.Column('category_id', sa.BigInteger(), nullable=False),
        sa.Column('sort_key', sa.String(300), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('page_id', 'category_id', name='uq_page_categories_page_cat'),
    )
    op.create_index('ix_page_categories_page_id', 'page_categories', ['page_id'], unique=False)
    op.create_index('ix_page_categories_category_id', 'page_categories', ['category_id'], unique=False)

    # 14. discussions (→ wikis, pages, users)
    op.create_table(
        'discussions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('page_id', sa.BigInteger(), nullable=False),
        sa.Column('author_id', sa.BigInteger(), nullable=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='open'),
        sa.Column('comment_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id']),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_discussions_wiki_id', 'discussions', ['wiki_id'], unique=False)
    op.create_index('ix_discussions_page_id', 'discussions', ['page_id'], unique=False)

    # 15. discussion_comments (→ discussions, users)
    op.create_table(
        'discussion_comments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('discussion_id', sa.BigInteger(), nullable=False),
        sa.Column('author_id', sa.BigInteger(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['discussion_id'], ['discussions.id']),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_discussion_comments_discussion_id', 'discussion_comments', ['discussion_id'], unique=False)

    # 16. edit_requests (→ wikis, pages, users)
    op.create_table(
        'edit_requests',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('page_id', sa.BigInteger(), nullable=False),
        sa.Column('requester_id', sa.BigInteger(), nullable=True),
        sa.Column('requester_ip', sa.String(45), nullable=True),
        sa.Column('original_content', sa.Text(), nullable=False, server_default=''),
        sa.Column('proposed_content', sa.Text(), nullable=False, server_default=''),
        sa.Column('comment', sa.String(500), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('reviewed_by', sa.BigInteger(), nullable=True),
        sa.Column('reject_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id']),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_edit_requests_wiki_id', 'edit_requests', ['wiki_id'], unique=False)
    op.create_index('ix_edit_requests_page_id', 'edit_requests', ['page_id'], unique=False)

    # 17. recent_changes (→ wikis, pages, users, page_revisions)
    op.create_table(
        'recent_changes',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('change_type', sa.String(20), nullable=False),
        sa.Column('page_id', sa.BigInteger(), nullable=True),
        sa.Column('page_title', sa.String(500), nullable=True),
        sa.Column('revision_id', sa.BigInteger(), nullable=True),
        sa.Column('actor_id', sa.BigInteger(), nullable=True),
        sa.Column('actor_name', sa.String(40), nullable=True),
        sa.Column('comment', sa.String(500), nullable=True),
        sa.Column('is_minor', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_bot', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('byte_diff', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, index=True),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id']),
        sa.ForeignKeyConstraint(['revision_id'], ['page_revisions.id']),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_recent_changes_wiki_id', 'recent_changes', ['wiki_id'], unique=False)

    # 18. search_index (→ wikis, pages)
    op.create_table(
        'search_index',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=False),
        sa.Column('page_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False, server_default=''),
        sa.Column('content_plain', sa.Text(), nullable=False, server_default=''),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wiki_id', 'page_id', name='uq_search_index_wiki_page'),
    )
    op.create_index('ix_search_index_wiki_id', 'search_index', ['wiki_id'], unique=False)
    op.create_index('ix_search_index_page_id', 'search_index', ['page_id'], unique=False)

    # 19. notifications (→ users, wikis)
    op.create_table(
        'notifications',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('wiki_id', sa.BigInteger(), nullable=True),
        sa.Column('type', sa.String(40), nullable=False),
        sa.Column('ref_id', sa.BigInteger(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['wiki_id'], ['wikis.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'], unique=False)


def downgrade() -> None:
    # 역순으로 삭제
    op.drop_table('notifications')
    op.drop_table('search_index')
    op.drop_table('recent_changes')
    op.drop_table('edit_requests')
    op.drop_table('discussion_comments')
    op.drop_table('discussions')
    op.drop_table('page_categories')
    op.drop_table('categories')
    op.drop_table('user_acl_overrides')
    op.drop_table('namespace_acls')
    op.drop_table('page_acls')
    op.drop_table('revision_suppressions')
    # pages.latest_revision_id FK 먼저 제거 (use_alter)
    op.drop_constraint('fk_pages_latest_revision', 'pages', type_='foreignkey')
    op.drop_table('page_revisions')
    op.drop_table('pages')
    op.drop_table('files')
    op.drop_table('blocks')
    op.drop_table('wiki_members')
    op.drop_table('wikis')
    op.drop_table('users')
