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
    const user = sessionStorage.getItem('user');
    if (token && user) {
      const parsedUser = JSON.parse(user);
      this.currentUser.set(parsedUser);
      this.isLoggedIn.set(true);
    } else if (token) {
      this.getUserProfile().subscribe({
        error: () => this.logout()
      });
    }
  }

  login(email: string, password: string): Observable<any> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, formData).pipe(
      tap(res => {
        sessionStorage.setItem('token', res.access_token);
      }),
      switchMap(() => this.getUserProfile())
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
    const role = data.role_id ?? 
                data.role ?? 
                (Array.isArray(data.role_ids) ? data.role_ids[0] : null);

    return role ? Number(role) : null;
  }

  logout() {
    sessionStorage.clear();
    this.currentUser.set(null);
    this.isLoggedIn.set(false);
    this.router.navigate(['/home']);
  }
}