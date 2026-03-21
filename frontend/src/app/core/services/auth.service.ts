import { Injectable, signal, inject } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = `${environment.apiUrl}/auth`;
  
  // State
  currentUser = signal<any>(null);
  isLoggedIn = signal(false);

  constructor() {
    this.checkAuth();
  }

  private checkAuth() {
    const token = sessionStorage.getItem('token');
    const user = sessionStorage.getItem('user');
    if (token && user) {
      this.currentUser.set(JSON.parse(user));
      this.isLoggedIn.set(true);
    } else {
      this.currentUser.set(null);
      this.isLoggedIn.set(false);
    }
  }

  login(email: string, password: string): Observable<LoginResponse> {
    const formData = new FormData();
    formData.append('username', email); // OAuth2 expects 'username' field
    formData.append('password', password);

    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, formData).pipe(
      tap(res => {
        sessionStorage.setItem('token', res.access_token);
        this.isLoggedIn.set(true);
        this.getUserProfile().subscribe();
      })
    );
  }

  getUserProfile(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/me`).pipe(
      tap(user => {
        sessionStorage.setItem('user', JSON.stringify(user));
        this.currentUser.set(user);
      })
    );
  }

  logout() {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    this.currentUser.set(null);
    this.isLoggedIn.set(false);
    // Auto redirect to home on logout
    this.router.navigate(['/home']);
  }
}
