from datetime import datetime
from flask import Blueprint, jsonify, request
from app.services.member_service import MemberService
from app.services.achievement_service import AchievementService
from app.services.kta_service import KtaService
from app.services.event_service import EventService
from app.repositories.in_memory.branches_repo import branches_repo

api_public_bp = Blueprint('api_public', __name__, url_prefix='/api/public')

@api_public_bp.after_request
def add_cors_headers(response):
    """
    Ensure all responses from this blueprint have permissive CORS headers,
    allowing external landing pages or client-side scripts to fetch data.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@api_public_bp.route('/', methods=['GET', 'OPTIONS'])
def api_index():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({
        'status': 'online',
        'name': 'Buana Nurraga Public API',
        'version': '1.0.0',
        'endpoints': {
            'stats': '/api/public/stats',
            'verify': '/api/public/verify/<nomor_induk>',
            'achievements': '/api/public/achievements',
            'branches': '/api/public/branches',
            'events': '/api/public/events'
        }
    })

@api_public_bp.route('/stats', methods=['GET', 'OPTIONS'])
def get_stats():
    """
    Public aggregated statistics:
    Total members, KTA issued, branches count, achievements, medals, and belt distributions.
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        members = MemberService.get_all_members()
        achievements = AchievementService.get_all_achievements()
        branches = branches_repo.get_all_branches()

        total_members = len(members)
        punya_kta = sum(1 for m in members if str(m.get('KTA', '')).strip().upper() == 'PUNYA')

        sabuk_counts = {}
        branch_counts = {}
        for m in members:
            sabuk = str(m.get('SABUK', '')).strip().upper()
            if sabuk:
                sabuk_counts[sabuk] = sabuk_counts.get(sabuk, 0) + 1
            cabang = str(m.get('CABANG', '')).strip().upper()
            if cabang:
                branch_counts[cabang] = branch_counts.get(cabang, 0) + 1

        total_emas = sum(1 for a in achievements if str(a.get('medali', '')).strip().lower() == 'emas')
        total_perak = sum(1 for a in achievements if str(a.get('medali', '')).strip().lower() == 'perak')
        total_perunggu = sum(1 for a in achievements if str(a.get('medali', '')).strip().lower() == 'perunggu')
        unique_athletes = len(set(str(a.get('nomor_induk', '')).strip() for a in achievements if a.get('nomor_induk')))

        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'total_members': total_members,
                'total_kta_issued': punya_kta,
                'total_branches': len(branches),
                'total_achievements': len(achievements),
                'unique_athletes': unique_athletes,
                'medals': {
                    'emas': total_emas,
                    'perak': total_perak,
                    'perunggu': total_perunggu
                },
                'belts': sabuk_counts,
                'branches': branch_counts
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_public_bp.route('/verify/<nomor_induk>', methods=['GET', 'OPTIONS'])
def verify_member(nomor_induk):
    """
    Public member/KTA verification endpoint.
    Sensitive personal information (NIK, phone, full address) is excluded for privacy.
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        member = MemberService.get_member_by_id(nomor_induk)
        now_str = datetime.now().strftime("%d %B %Y, %H:%M:%S WITA")

        if not member:
            return jsonify({
                'status': 'fail',
                'valid': False,
                'nomor_induk': str(nomor_induk).strip(),
                'checked_at': now_str,
                'message': f'Nomor Induk {nomor_induk} tidak terdaftar dalam pangkalan data resmi.'
            }), 404

        sabuk = str(member.get('SABUK', 'HIJAU')).strip().upper()
        belt_info = KtaService.get_belt_info(sabuk)

        tanggal_sah = member.get(sabuk)
        if not tanggal_sah or str(tanggal_sah).strip() == '':
            tanggal_sah = member.get('HIJAU') or member.get('TANGGAL') or '25 Mei 2025'

        # Fetch achievements for this member
        achievements = AchievementService.get_achievements_by_nomor_induk(nomor_induk)

        member_data = {
            'nomor_induk': str(member.get('NOMOR INDUK', '')).strip(),
            'nama_lengkap': str(member.get('NAMA LENGKAP', '')).strip().upper(),
            'sabuk': sabuk,
            'belt_info': belt_info,
            'cabang': str(member.get('CABANG', '-')).strip(),
            'kabupaten': str(member.get('KABUPATEN/KOTA', member.get('CABANG', '-'))).strip(),
            'tanggal_sah': str(tanggal_sah).strip(),
            'photo_url': member.get('FOTO_URL') or '/static/img/avatar_placeholder.svg',
            'status_kta': str(member.get('KTA', 'BELUM')).strip().upper(),
            'achievements': achievements
        }

        return jsonify({
            'status': 'success',
            'valid': True,
            'checked_at': now_str,
            'data': member_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_public_bp.route('/achievements', methods=['GET', 'OPTIONS'])
def get_achievements():
    """
    Public achievements list with optional filters by medali, branch, tingkat, and search keyword.
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        achievements = AchievementService.get_all_achievements()
        members = MemberService.get_all_members()
        member_map = {str(m.get('NOMOR INDUK', '')).strip(): m for m in members}

        enriched_achievements = []
        for ach in achievements:
            member = member_map.get(str(ach.get('nomor_induk', '')).strip(), {})
            item = dict(ach)
            item['nama_lengkap'] = member.get('NAMA LENGKAP', 'Atlet Buana Nurraga')
            item['cabang'] = member.get('CABANG', '-')
            item['sabuk'] = member.get('SABUK', '-')
            item['athlete_photo'] = member.get('FOTO_URL') or '/static/img/avatar_placeholder.svg'
            if not item.get('photo_url'):
                item['photo_url'] = member.get('FOTO_URL') or None
            # Strip internal user metadata
            item.pop('created_by', None)
            enriched_achievements.append(item)

        # Filters from query params
        medali_filter = request.args.get('medali', '').strip().lower()
        branch_filter = request.args.get('branch', '').strip().upper()
        tingkat_filter = request.args.get('tingkat', '').strip().lower()
        search_query = request.args.get('search', '').strip().lower()

        filtered = enriched_achievements

        if medali_filter:
            filtered = [a for a in filtered if str(a.get('medali', '')).strip().lower() == medali_filter]
        if branch_filter:
            filtered = [a for a in filtered if str(a.get('cabang', '')).strip().upper() == branch_filter]
        if tingkat_filter:
            filtered = [a for a in filtered if str(a.get('tingkat', '')).strip().lower() == tingkat_filter]
        if search_query:
            filtered = [
                a for a in filtered
                if search_query in str(a.get('nama_lengkap', '')).lower()
                or search_query in str(a.get('nama_kejuaraan', '')).lower()
                or search_query in str(a.get('kategori', '')).lower()
            ]

        # Optional limit
        limit = request.args.get('limit', type=int)
        if limit and limit > 0:
            filtered = filtered[:limit]

        return jsonify({
            'status': 'success',
            'total': len(filtered),
            'data': filtered
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_public_bp.route('/branches', methods=['GET', 'OPTIONS'])
def get_branches():
    """
    Public branches directory with member counts per branch.
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        branches = branches_repo.get_all_branches()
        members = MemberService.get_all_members()

        branch_counts = {}
        for m in members:
            cabang = str(m.get('CABANG', '')).strip().upper()
            if cabang:
                branch_counts[cabang] = branch_counts.get(cabang, 0) + 1

        result = []
        for b in branches:
            b_copy = dict(b)
            name_upper = b.get('branch_name', '').upper()
            b_copy['total_members'] = branch_counts.get(name_upper, 0)
            result.append(b_copy)

        return jsonify({
            'status': 'success',
            'total': len(result),
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_public_bp.route('/events', methods=['GET', 'OPTIONS'])
def get_events():
    """
    Public upcoming and active events list for landing page.
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        events = EventService.get_active_events()
        category_filter = request.args.get('category', '').strip().lower()
        search_query = request.args.get('search', '').strip().lower()

        data = [e.to_dict() for e in events]

        if category_filter:
            data = [e for e in data if str(e.get('category', '')).strip().lower() == category_filter]

        if search_query:
            data = [
                e for e in data 
                if search_query in str(e.get('title', '')).lower() 
                or search_query in str(e.get('location', '')).lower()
                or search_query in str(e.get('description', '')).lower()
            ]

        return jsonify({
            'status': 'success',
            'total': len(data),
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_public_bp.route('/instagram-feed', methods=['GET', 'OPTIONS'])
def get_instagram_feed():
    """
    Public Instagram curated feed & documentation for landing page.
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        from app.services.gallery_service import GalleryService
        posts = GalleryService.get_active_posts()
        category_filter = request.args.get('category', '').strip().lower()
        limit = request.args.get('limit', type=int)

        data = [p.to_dict() for p in posts]

        if category_filter:
            data = [
                p for p in data 
                if category_filter in str(p.get('category_slug', '')).lower() 
                or category_filter in str(p.get('category', '')).lower()
            ]

        if limit and limit > 0:
            data = data[:limit]

        return jsonify({
            'status': 'success',
            'total': len(data),
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
