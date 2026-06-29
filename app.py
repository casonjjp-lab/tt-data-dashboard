from supabase import create_client
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, date
import os
from openpyxl import load_workbook

# ==================== Supabase 配置 ====================
SUPABASE_URL = 'https://tbxxhmtqufzzhshivija.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRieHhobXRxdWZ6emhzaGl2aWphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjcxMDY1MCwiZXhwIjoyMDk4Mjg2NjUwfQ.uYnFvitNn_CrqXCvXu0xGLEF994uxMrUeINYwjPf8Eg'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==================== Flask 应用初始化 ====================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tt-data-management-system'
CORS(app)

os.makedirs('uploads', exist_ok=True)

# ==================== 辅助函数 ====================

def parse_date(date_str):
    if isinstance(date_str, date):
        return date_str
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def ad_to_dict(a):
    return {
        'id': a['id'],
        'date': a['date'],
        'pkg': a['pkg'],
        'group': a['group'],
        'panel': a['panel'],
        'spend': a['spend'],
        'spendClean': a['spend_clean'],
        'revenue': a['revenue'],
        'created_at': a.get('created_at', '')
    }

def rev_to_dict(r):
    return {
        'id': r['id'],
        'date': r['date'],
        'installDays': r['install_days'],
        'coin': r['coin'],
        'firstSub': r['first_sub'],
        'renewSub': r['renew_sub'],
        'coinRenew': r['coin_renew'],
        'total': r['total'],
        'created_at': r.get('created_at', '')
    }

def build_ad_filters(filters):
    query = supabase.table('ads').select('*')
    if filters.get('startDate'):
        query = query.gte('date', filters['startDate'])
    if filters.get('endDate'):
        query = query.lte('date', filters['endDate'])
    if filters.get('pkg'):
        query = query.eq('pkg', filters['pkg'])
    if filters.get('group'):
        query = query.eq('group', filters['group'])
    if filters.get('panel'):
        query = query.eq('panel', filters['panel'])
    return query

def build_rev_filters(filters):
    query = supabase.table('revenues').select('*')
    if filters.get('startDate'):
        query = query.gte('date', filters['startDate'])
    if filters.get('endDate'):
        query = query.lte('date', filters['endDate'])
    if filters.get('installDays'):
        query = query.eq('install_days', str(filters['installDays']))
    return query

# ==================== 前端页面路由 ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/history')
def history():
    return render_template('history.html')

# ==================== API 路由 ====================

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# ==================== 投放数据 API ====================

@app.route('/api/ads', methods=['GET'])
def get_ads():
    try:
        filters = {
            'startDate': request.args.get('startDate'),
            'endDate': request.args.get('endDate'),
            'pkg': request.args.get('pkg'),
            'group': request.args.get('group'),
            'panel': request.args.get('panel')
        }
        query = build_ad_filters(filters)
        res = query.order('date', desc=True).order('id', desc=True).execute()
        return jsonify({'success': True, 'data': [ad_to_dict(a) for a in res.data]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ads', methods=['POST'])
def create_ad():
    try:
        data = request.json
        payload = {
            'date': data['date'],
            'pkg': data['pkg'],
            'group': data['group'],
            'panel': data['panel'],
            'spend': float(data.get('spend', 0)),
            'spend_clean': float(data.get('spendClean', 0)),
            'revenue': float(data.get('revenue', 0))
        }
        res = supabase.table('ads').insert(payload).execute()
        return jsonify({'success': True, 'id': res.data[0]['id']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ads/batch', methods=['POST'])
def create_ads_batch():
    try:
        data_list = request.json.get('data', [])
        payload = [{
            'date': d['date'],
            'pkg': d['pkg'],
            'group': d['group'],
            'panel': d['panel'],
            'spend': float(d.get('spend', 0)),
            'spend_clean': float(d.get('spendClean', 0)),
            'revenue': float(d.get('revenue', 0))
        } for d in data_list]
        res = supabase.table('ads').insert(payload).execute()
        return jsonify({'success': True, 'count': len(res.data)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ads/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    try:
        supabase.table('ads').delete().eq('id', ad_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ads/delete-batch', methods=['POST'])
def delete_ads_batch():
    try:
        ids = request.json.get('ids', [])
        for ad_id in ids:
            supabase.table('ads').delete().eq('id', ad_id).execute()
        return jsonify({'success': True, 'deleted': len(ids)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 收入数据 API ====================

@app.route('/api/revenues', methods=['GET'])
def get_revenues():
    try:
        filters = {
            'startDate': request.args.get('startDate'),
            'endDate': request.args.get('endDate'),
            'installDays': request.args.get('installDays')
        }
        query = build_rev_filters(filters)
        res = query.order('date', desc=True).order('id', desc=True).execute()
        return jsonify({'success': True, 'data': [rev_to_dict(r) for r in res.data]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/revenues', methods=['POST'])
def create_revenue():
    try:
        data = request.json
        payload = {
            'date': data['date'],
            'install_days': str(data['installDays']),
            'coin': float(data.get('coin', 0)),
            'first_sub': float(data.get('firstSub', 0)),
            'renew_sub': float(data.get('renewSub', 0)),
            'coin_renew': float(data.get('coinRenew', 0)),
            'total': float(data.get('total', 0))
        }
        res = supabase.table('revenues').insert(payload).execute()
        return jsonify({'success': True, 'id': res.data[0]['id']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/revenues/batch', methods=['POST'])
def create_revenues_batch():
    try:
        data_list = request.json.get('data', [])
        payload = [{
            'date': d['date'],
            'install_days': str(d['installDays']),
            'coin': float(d.get('coin', 0)),
            'first_sub': float(d.get('firstSub', 0)),
            'renew_sub': float(d.get('renewSub', 0)),
            'coin_renew': float(d.get('coinRenew', 0)),
            'total': float(d.get('total', 0))
        } for d in data_list]
        res = supabase.table('revenues').insert(payload).execute()
        return jsonify({'success': True, 'count': len(res.data)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/revenues/<int:rev_id>', methods=['DELETE'])
def delete_revenue(rev_id):
    try:
        supabase.table('revenues').delete().eq('id', rev_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/revenues/delete-batch', methods=['POST'])
def delete_revenues_batch():
    try:
        ids = request.json.get('ids', [])
        for rev_id in ids:
            supabase.table('revenues').delete().eq('id', rev_id).execute()
        return jsonify({'success': True, 'deleted': len(ids)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 统计数据 API ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        filters = {
            'startDate': request.args.get('startDate'),
            'endDate': request.args.get('endDate'),
            'pkg': request.args.get('pkg'),
            'group': request.args.get('group'),
            'panel': request.args.get('panel')
        }
        query = build_ad_filters(filters)
        res = query.execute()
        ads = res.data

        total_spend = sum(a['spend'] for a in ads)
        total_spend_clean = sum(a['spend_clean'] for a in ads)
        total_revenue = sum(a['revenue'] for a in ads)

        roi = (total_revenue / total_spend) if total_spend > 0 else 0
        roi_clean = (total_revenue / total_spend_clean) if total_spend_clean > 0 else 0

        return jsonify({
            'success': True,
            'data': {
                'totalSpend': total_spend,
                'totalSpendClean': total_spend_clean,
                'totalRevenue': total_revenue,
                'roi': roi,
                'roiClean': roi_clean
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    try:
        filters = {
            'startDate': request.args.get('startDate'),
            'endDate': request.args.get('endDate'),
            'pkg': request.args.get('pkg'),
            'group': request.args.get('group'),
            'panel': request.args.get('panel')
        }
        query = build_ad_filters(filters)
        res = query.order('date', asc=True).execute()
        ads = res.data

        date_summary = {}
        for ad in ads:
            d = ad['date']
            if d not in date_summary:
                date_summary[d] = {'spend': 0, 'spendClean': 0, 'revenue': 0}
            date_summary[d]['spend'] += ad['spend']
            date_summary[d]['spendClean'] += ad['spend_clean']
            date_summary[d]['revenue'] += ad['revenue']

        chart_data = []
        for d in sorted(date_summary.keys()):
            s = date_summary[d]
            roi = (s['revenue'] / s['spend']) if s['spend'] > 0 else 0
            roi_clean = (s['revenue'] / s['spendClean']) if s['spendClean'] > 0 else 0
            chart_data.append({
                'date': d,
                'spend': s['spend'],
                'spendClean': s['spendClean'],
                'revenue': s['revenue'],
                'roi': roi,
                'roiClean': roi_clean
            })

        return jsonify({'success': True, 'data': chart_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Excel 导入 API ====================

def read_excel_data(file):
    filename = file.filename
    if filename.endswith('.csv'):
        import csv
        from io import StringIO
        stream = StringIO(file.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        return list(reader)
    else:
        wb = load_workbook(filename=file, data_only=True)
        ws = wb.active
        headers = [cell.value for cell in ws[1]]
        data = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    row_dict[headers[i]] = value
            if any(row_dict.values()):
                data.append(row_dict)
        return data

@app.route('/api/import/ad', methods=['POST'])
def import_ad_excel():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        data_list = read_excel_data(file)
        payload = []
        for row in data_list:
            payload.append({
                'date': str(row.get('投放日期') or row.get('date')),
                'pkg': str(row.get('包名') or row.get('pkg')),
                'group': str(row.get('投放组') or row.get('group')),
                'panel': str(row.get('面板') or row.get('panel')),
                'spend': float(row.get('消耗') or row.get('spend') or 0),
                'spend_clean': float(row.get('消耗去空耗') or row.get('spendClean') or 0),
                'revenue': float(row.get('收入投放口径') or row.get('revenue') or 0)
            })
        res = supabase.table('ads').insert(payload).execute()
        return jsonify({'success': True, 'count': len(res.data)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/import/revenue', methods=['POST'])
def import_revenue_excel():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        data_list = read_excel_data(file)
        payload = []
        for row in data_list:
            coin = float(row.get('金币收入') or row.get('coin') or 0)
            first_sub = float(row.get('会员首订') or row.get('firstSub') or 0)
            renew_sub = float(row.get('会员续订') or row.get('renewSub') or 0)
            coin_renew = float(row.get('金币续订') or row.get('coinRenew') or 0)
            payload.append({
                'date': str(row.get('投放日期') or row.get('date')),
                'install_days': str(row.get('天数') or row.get('installDays') or '0'),
                'coin': coin,
                'first_sub': first_sub,
                'renew_sub': renew_sub,
                'coin_renew': coin_renew,
                'total': coin + first_sub + renew_sub + coin_renew
            })
        res = supabase.table('revenues').insert(payload).execute()
        return jsonify({'success': True, 'count': len(res.data)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 宽表 API ====================

@app.route('/api/wide-table', methods=['GET'])
def get_wide_table():
    try:
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')

        ad_query = supabase.table('ads').select('*')
        if start_date:
            ad_query = ad_query.gte('date', start_date)
        if end_date:
            ad_query = ad_query.lte('date', end_date)
        ads_res = ad_query.execute()
        ads = ads_res.data

        ad_by_date = {}
        for ad in ads:
            d = ad['date']
            if d not in ad_by_date:
                ad_by_date[d] = {'spend': 0.0, 'spend_clean': 0.0, 'revenue': 0.0}
            ad_by_date[d]['spend'] += ad['spend']
            ad_by_date[d]['spend_clean'] += ad['spend_clean']
            ad_by_date[d]['revenue'] += ad['revenue']

        rev_query = supabase.table('revenues').select('*')
        if start_date:
            rev_query = rev_query.gte('date', start_date)
        if end_date:
            rev_query = rev_query.lte('date', end_date)
        rev_res = rev_query.execute()
        revenues = rev_res.data

        rev_by_date = {}
        for rev in revenues:
            d = rev['date']
            days = str(rev['install_days'])
            if d not in rev_by_date:
                rev_by_date[d] = {}
            if days not in rev_by_date[d]:
                rev_by_date[d][days] = {'coin': 0.0, 'firstSub': 0.0, 'renewSub': 0.0, 'coinRenew': 0.0, 'total': 0.0}
            rev_by_date[d][days]['coin'] += rev['coin']
            rev_by_date[d][days]['firstSub'] += rev['first_sub']
            rev_by_date[d][days]['renewSub'] += rev['renew_sub']
            rev_by_date[d][days]['coinRenew'] += rev['coin_renew']
            rev_by_date[d][days]['total'] += rev['total']

        all_dates = sorted(set(list(ad_by_date.keys()) + list(rev_by_date.keys())), reverse=True)

        DAYS_LIST = ['0', '8', '14', '30', '45']
        DAYS_KEY  = {'0': 'day0', '8': 'day8', '14': 'day14', '30': 'day30', '45': 'day45'}

        rows = []
        for d in all_dates:
            ad = ad_by_date.get(d, {'spend': 0.0, 'spend_clean': 0.0, 'revenue': 0.0})
            spend = ad['spend']
            spend_clean = ad['spend_clean']
            revenue = ad['revenue']
            roi = revenue / spend if spend > 0 else None
            roi_clean = revenue / spend_clean if spend_clean > 0 else None

            row = {
                'date': d,
                'spend': spend,
                'spendClean': spend_clean,
                'revenue': revenue,
                'roi': roi,
                'roiClean': roi_clean,
            }

            for days in DAYS_LIST:
                key = DAYS_KEY[days]
                rev_days = rev_by_date.get(d, {}).get(days, {})
                if days == '0':
                    row[f'{key}_coin'] = rev_days.get('coin', 0.0)
                    row[f'{key}_firstSub'] = rev_days.get('firstSub', 0.0)
                    row[f'{key}_renewSub'] = rev_days.get('renewSub', 0.0)
                    row[f'{key}_total'] = rev_days.get('total', 0.0)
                else:
                    row[f'{key}_coinRenew'] = rev_days.get('coinRenew', 0.0)
                    row[f'{key}_renewSub'] = rev_days.get('renewSub', 0.0)
                    row[f'{key}_total'] = rev_days.get('total', 0.0)

            rows.append(row)

        return jsonify({'success': True, 'data': rows, 'total': len(rows)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 静态文件服务 ====================

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ==================== 启动应用 ====================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
