import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, switchMap } from 'rxjs';
import { Router } from '@angular/router';
import { VerifyOTPRequest } from '../../core/models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/v1/auth';
  private tokenKey = 'token';
  private userKey = 'user';

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {}

  login(email: string, password: string, returnUrl: string = '/home'): Observable<any> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);

    return this.http.post<any>(`${this.apiUrl}/login`, body.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).pipe(
      tap((res) => {
        this.setToken(res.access_token);
      }),
      switchMap(() => this.getUserProfile()),
      tap(() => {
        const role = this.getUserRole();
        if (role === 1) {
          this.router.navigate(['/admin/dashboard']);
        } else if (role === 2) {
          this.router.navigate(['/moderator/dashboard']);
        } else {
          this.router.navigate([returnUrl || '/home']);
        }
      })
    );
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, userData);
  }

  logout(): void {
    sessionStorage.removeItem(this.tokenKey);
    sessionStorage.removeItem(this.userKey);
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/']);
  }

  getUserProfile(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/me`).pipe(
      tap((user) => {
        this.setUserData(user);
      })
    );
  }

  setToken(token: string): void {
    sessionStorage.setItem(this.tokenKey, token);
    this.isAuthenticatedSubject.next(true);
  }

  getToken(): string | null {
    return sessionStorage.getItem(this.tokenKey);
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  isAuthenticated(): boolean {
    return this.hasToken();
  }

  setUserData(userData: any): void {
    sessionStorage.setItem(this.userKey, JSON.stringify(userData));
  }

  getUserData(): any {
    const data = sessionStorage.getItem(this.userKey);
    return data ? JSON.parse(data) : null;
  }

  getUserRole(): number | null {
    const userData = this.getUserData();

    if (!userData) {
      return null;
    }

    let roleValue: any = null;
    if (userData.role_id !== undefined && userData.role_id !== null) {
      roleValue = userData.role_id;
    } else if (userData.role && userData.role.role_id !== undefined) {
      roleValue = userData.role.role_id;
    } else if (Array.isArray(userData.role_ids) && userData.role_ids.length > 0) {
      roleValue = userData.role_ids[0];
    }

    const roleNumber = Number(roleValue);
    return Number.isInteger(roleNumber) ? roleNumber : null;
  }
}