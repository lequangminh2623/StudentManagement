"""Initial migration

Revision ID: 2b0649f4a574
Revises: 
Create Date: 2024-12-18 14:18:19.065138

"""
from email.policy import default

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b0649f4a574'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('application_form',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('gender', sa.Boolean(), nullable=False),
    sa.Column('phone', sa.String(length=10), nullable=False),
    sa.Column('address', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', name='applicationformstatus'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('rule',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('rule_name', sa.String(length=50), nullable=False),
    sa.Column('min_value', sa.Integer(), nullable=True),
    sa.Column('max_value', sa.Integer(), nullable=True),
    sa.Column('rule_content', sa.String(length=500), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('rule_content'),
    sa.UniqueConstraint('rule_name')
    )
    op.create_table('school_year',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('school_year_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('school_year_name')
    )
    op.create_table('subject',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('subject_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subject_name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('avatar', sa.String(length=100), nullable=True),
    sa.Column('role', sa.Enum('ADMIN', 'STAFF', 'TEACHER', 'STUDENT', name='role'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('admin_info',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('gender', sa.Boolean(), nullable=False),
    sa.Column('phone', sa.String(length=10), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('grade',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('grade_name', sa.Enum('GRADE10', 'GRADE11', 'GRADE12', name='gradetype'), nullable=False),
    sa.Column('school_year_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['school_year_id'], ['school_year.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('grade_name', 'school_year_id', name='uq_gradename_schoolyearid')
    )
    op.create_table('semester',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('semester_name', sa.Enum('FIRSTTERM', 'SECONDTERM', name='semestertype'), nullable=False),
    sa.Column('school_year_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['school_year_id'], ['school_year.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('semester_name', 'school_year_id', name='uq_semestername_schoolyearid')
    )
    op.create_table('staff_info',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('gender', sa.Boolean(), nullable=False),
    sa.Column('phone', sa.String(length=10), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('student_info',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('application_form_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('gender', sa.Boolean(), nullable=False),
    sa.Column('phone', sa.String(length=10), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['application_form_id'], ['application_form.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('application_form_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('teacher_info',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('gender', sa.Boolean(), nullable=False),
    sa.Column('phone', sa.String(length=10), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('classroom',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('classroom_name', sa.String(length=50), nullable=False),
    sa.Column('student_number', sa.Integer(), nullable=False, default=0),
    sa.Column('grade_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['grade_id'], ['grade.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('classroom_name', 'grade_id', name='uq_classroomname_gradeid')
    )
    op.create_table('curriculum',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('curriculum_name', sa.String(length=50), nullable=False),
    sa.Column('grade_id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['grade_id'], ['grade.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('grade_id', 'subject_id', name='uq_gradeid_subjectid')
    )
    op.create_table('report',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('report_name', sa.String(length=50), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.Column('semester_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['semester_id'], ['semester.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subject_id', 'semester_id', name='uq_subjectid_semesterid')
    )
    op.create_table('classroom_transfer',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('is_classroom_changed', sa.Boolean(), nullable=False),
    sa.Column('transfer_date', sa.Date(), nullable=False),
    sa.Column('classroom_id', sa.Integer(), nullable=False),
    sa.Column('student_info_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['classroom_id'], ['classroom.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['student_info_id'], ['student_info.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_info_id', 'classroom_id', 'transfer_date', name='uq_studentinfoid_classroom_transferdate')
    )
    op.create_table('statistic',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('pass_count', sa.Integer(), nullable=False),
    sa.Column('pass_rate', sa.Float(), nullable=False),
    sa.Column('classroom_id', sa.Integer(), nullable=False),
    sa.Column('report_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['classroom_id'], ['classroom.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['report_id'], ['report.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('classroom_id', 'report_id', name='uq_classroomid_reportid')
    )
    op.create_table('transcript',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('transcript_name', sa.String(length=50), nullable=False),
    sa.Column('is_done', sa.Boolean(), nullable=False),
    sa.Column('classroom_id', sa.Integer(), nullable=False),
    sa.Column('curriculum_id', sa.Integer(), nullable=False),
    sa.Column('semester_id', sa.Integer(), nullable=False),
    sa.Column('teacher_info_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['classroom_id'], ['classroom.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['curriculum_id'], ['curriculum.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['semester_id'], ['semester.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['teacher_info_id'], ['teacher_info.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('classroom_id', 'curriculum_id', 'semester_id', name='uq_classroomid_curriculumid_semesterid')
    )
    op.create_table('exam_score',
    sa.Column('student_info_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('transcript_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_info_id'], ['student_info.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['transcript_id'], ['transcript.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fifteen_minute_score',
    sa.Column('student_info_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('transcript_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_info_id'], ['student_info.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['transcript_id'], ['transcript.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('first_term_average_score',
    sa.Column('student_info_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('transcript_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_info_id'], ['student_info.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['transcript_id'], ['transcript.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('one_period_score',
    sa.Column('student_info_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('transcript_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_info_id'], ['student_info.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['transcript_id'], ['transcript.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('second_term_average_score',
    sa.Column('student_info_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('transcript_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_info_id'], ['student_info.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['transcript_id'], ['transcript.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('second_term_average_score')
    op.drop_table('one_period_score')
    op.drop_table('first_term_average_score')
    op.drop_table('fifteen_minute_score')
    op.drop_table('exam_score')
    op.drop_table('transcript')
    op.drop_table('statistic')
    op.drop_table('classroom_transfer')
    op.drop_table('report')
    op.drop_table('curriculum')
    op.drop_table('classroom')
    op.drop_table('teacher_info')
    op.drop_table('student_info')
    op.drop_table('staff_info')
    op.drop_table('semester')
    op.drop_table('grade')
    op.drop_table('admin_info')
    op.drop_table('user')
    op.drop_table('subject')
    op.drop_table('school_year')
    op.drop_table('rule')
    op.drop_table('application_form')
    # ### end Alembic commands ###
