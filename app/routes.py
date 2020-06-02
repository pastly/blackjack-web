from flask import render_template, current_app


def my_render_template(*a, **kw):
    kw.update({
        'analytics': not not current_app.config['ANALYTICS'],
    })
    return render_template(*a, **kw)
