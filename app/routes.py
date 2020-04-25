from flask import render_template, current_app


def my_render_template(*a, **kw):
    kw.update({
        'google_analytics_id': current_app.config['GOOGLE_ANALYTICS'],
    })
    return render_template(*a, **kw)
