from .models import Usuario, Empresa, Administrador

def usuario_actual(request):
    context = {}
    if request.session.get('user_id'):
        user_type = request.session.get('user_type')
        user_id = request.session.get('user_id')
        
        if user_type == 'usuario':
            try:
                context['usuario'] = Usuario.objects.get(id=user_id)
            except Usuario.DoesNotExist:
                pass
        elif user_type == 'empresa':
            try:
                context['empresa'] = Empresa.objects.get(id=user_id)
            except Empresa.DoesNotExist:
                pass
        elif user_type == 'administrador':
            try:
                context['administrador'] = Administrador.objects.get(id=user_id)
            except Administrador.DoesNotExist:
                pass
    return context