from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, SpeakingExercise, UserSpeakingProgress
from datetime import datetime

speaking_bp = Blueprint('speaking', __name__, url_prefix='/speaking')

# 口语练习列表页
@speaking_bp.route('/')
@login_required
def index():
    exercises = SpeakingExercise.query.order_by(SpeakingExercise.difficulty).all()
    return render_template('speaking/index.html', exercises=exercises)

# 单个口语练习详情页
@speaking_bp.route('/exercise/<int:exercise_id>')
@login_required
def exercise_detail(exercise_id):
    exercise = SpeakingExercise.query.get_or_404(exercise_id)
    # 获取用户该练习的进度
    progress = UserSpeakingProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()
    return render_template('speaking/detail.html', exercise=exercise, progress=progress)

# 提交口语练习（示例：仅记录进度，录音功能需额外实现）
@speaking_bp.route('/submit/<int:exercise_id>', methods=['POST'])
@login_required
def submit_exercise(exercise_id):
    exercise = SpeakingExercise.query.get_or_404(exercise_id)
    # 模拟接收录音URL（实际项目中需结合文件上传）
    audio_url = request.form.get('audio_url', '')
    feedback = request.form.get('feedback', '')
    score = request.form.get('score', 0.0)

    # 更新/创建用户进度
    progress = UserSpeakingProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()

    if progress:
        progress.audio_url = audio_url
        progress.score = float(score)
        progress.feedback = feedback
        progress.completed = True
        progress.submitted_at = datetime.utcnow()
    else:
        progress = UserSpeakingProgress(
            user_id=current_user.id,
            exercise_id=exercise_id,
            audio_url=audio_url,
            score=float(score),
            feedback=feedback,
            completed=True,
            submitted_at=datetime.utcnow()
        )
        db.session.add(progress)
    
    db.session.commit()
    flash('Speaking exercise submitted successfully!', 'success')
    return redirect(url_for('speaking.exercise_detail', exercise_id=exercise_id))