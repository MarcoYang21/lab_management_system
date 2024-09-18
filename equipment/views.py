# equipment/views.py
from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ReservationForm
from .models import User, Equipment, Reservation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def borrow_equipment(request):
    # 實現借用設備邏輯
    return render(request, 'equipment/reservation_form.html')

@login_required
def my_borrowed_equipment(request):
    # 實現查看已借用設備邏輯
    return render(request, 'equipment/my_borrowed_equipment.html')

@login_required
def profile(request):
    return render(request, 'equipment/profile.html')

def register(request):
    # 實現註冊邏輯
    return render(request, 'equipment/register.html')

def home(request):
    return render(request, 'equipment/home.html')

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "註冊成功！")
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'equipment/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"您已登入為 {username}。")
                return redirect('profile')
            else:
                messages.error(request, "無效的用戶名或密碼。")
        else:
            messages.error(request, "無效的用戶名或密碼。")
    form = CustomAuthenticationForm()
    return render(request, 'equipment/login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'equipment/profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    messages.info(request, "您已成功登出。")
    return redirect('login')

class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'equipments'
    paginate_by = 10  # 每頁顯示10個設備

class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = 'equipment/equipment_detail.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 這裡可以添加額外的上下文數據，例如相關的預約信息
        context['reservations'] = self.object.reservation_set.all()[:5]  # 顯示最近的5個預約
        return context
    
class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'equipment/reservation_form.html'
    success_url = reverse_lazy('equipment_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.equipment = get_object_or_404(Equipment, pk=self.kwargs['equipment_pk'])
        messages.success(self.request, '預約成功創建！')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipment'] = get_object_or_404(Equipment, pk=self.kwargs['equipment_pk'])
        return context