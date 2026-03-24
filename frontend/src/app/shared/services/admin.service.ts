import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private apiUrl = `${environment.apiUrl}`;

  constructor(private http: HttpClient) {}

  // Dashboard Stats
  getStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/admin/stats`);
  }

  // User Management
  getUsers(skip: number = 0, limit: number = 20): Observable<any[]> {
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    return this.http.get<any[]>(`${this.apiUrl}/admin/users`, { params });
  }

  banUser(userId: number, reason: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/moderator/users/${userId}/ban`, { reason });
  }

  unbanUser(userId: number, reason: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/moderator/users/${userId}/unban`, { reason });
  }

  deleteUser(userId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/users/${userId}`);
  }

  // Feedback Management
  getFeedbacks(skip: number = 0, limit: number = 100): Observable<any[]> {
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    return this.http.get<any[]>(`${this.apiUrl}/admin/feedbacks`, { params });
  }

  updateFeedbackStatus(feedbackId: number, status: number): Observable<any> {
    let params = new HttpParams().set('status_update', status.toString());
    return this.http.patch(`${this.apiUrl}/admin/feedbacks/${feedbackId}`, {}, { params });
  }

  // Category Management
  getCategories(activeOnly: boolean = false, includeDeleted: boolean = false): Observable<any[]> {
    let params = new HttpParams()
      .set('active_only', activeOnly.toString())
      .set('include_deleted', includeDeleted.toString());
    return this.http.get<any[]>(`${this.apiUrl}/categories`, { params });
  }

  createCategory(category: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/categories`, category);
  }

  updateCategory(categoryId: number, category: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/categories/${categoryId}`, category);
  }

  deleteCategory(categoryId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/categories/${categoryId}`);
  }

  hardDeleteCategory(categoryId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/categories/${categoryId}/hard-delete`);
  }

  restoreCategory(categoryId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/categories/${categoryId}/restore`, {});
  }
}
