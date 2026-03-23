import { Injectable, signal, inject } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, switchMap, of } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = `${environment.apiUrl}/auth`;

  currentUser = signal<any>(null);
  isLoggedIn = signal(false);

  constructor() {
    this.checkAuth();
  }

  private checkAuth() {
    const token = sessionStorage.getItem('token');
    const cachedUser = sessionStorage.getItem('user');

    if (!token) {
      this.currentUser.set(null);
      this.isLoggedIn.set(false);
      return;
    }

    if (cachedUser) {
      try {
        this.currentUser.set(JSON.parse(cachedUser));
        this.isLoggedIn.set(true);
      } catch {
        sessionStorage.removeItem('user');
      }
    }

    // Luôn refresh user từ API /me để tránh dữ liệu cũ trong sessionStorage
    this.getUserProfile().subscribe({
      error: () => this.logout()
    });
  }

  login(email: string, password: string, returnUrl: string = '/home'): Observable<any> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, formData).pipe(
      tap(res => {
        sessionStorage.setItem('token', res.access_token);
      }),
      switchMap(() => this.getUserProfile()),
      tap((user) => {
        const roleId = Number(user.role_id);
        if (roleId === 1) {
          this.router.navigate(['/admin/dashboard']);
        } else if (roleId === 2) {
          this.router.navigate(['/moderator/dashboard']);
        } else {
          this.router.navigate(['/home']);
        }
      })
    );
  }

  getUserProfile(): Observable<any> {
    const token = sessionStorage.getItem('token');
    return this.http.get<any>(`${this.apiUrl}/me`).pipe(
      tap(user => {
        sessionStorage.setItem('user', JSON.stringify(user));
        this.currentUser.set(user);
        this.isLoggedIn.set(true);
      })
    );
  }

  isAuthenticated(): boolean {
    return !!sessionStorage.getItem('token');
  }

  getUserRole(): number | null {
    const user = this.currentUser();
    const data = user ? user : JSON.parse(sessionStorage.getItem('user') || '{}');

    if (data && data.role_id !== undefined && data.role_id !== null) {
      return Number(data.role_id);
    }

    return null;
  }

  logout() {
    sessionStorage.clear();
    this.currentUser.set(null);
    this.isLoggedIn.set(false);
    this.router.navigate(['/home']);
  }
}