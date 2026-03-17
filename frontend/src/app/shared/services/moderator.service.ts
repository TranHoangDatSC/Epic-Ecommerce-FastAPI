import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ProductApprovalRequest {
  status: number;
  reject_reason?: string;
}

export interface ViolationReportRequest {
  review_id: number;
}

export interface UserBanRequest {
  reason: string;
}

@Injectable({
  providedIn: 'root'
})
export class ModeratorService {
  private apiUrl = `${environment.apiUrl}/moderator`;

  constructor(private http: HttpClient) {}

  // Product moderation
  getPendingProducts(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/products/pending`);
  }

  getRejectedProducts(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/products/rejected`);
  }

  getArchivedProducts(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/products/archived`);
  }

  approveProduct(productId: number, status: number, rejectReason?: string): Observable<any> {
    const body: ProductApprovalRequest = { status };
    if (rejectReason) {
      body.reject_reason = rejectReason;
    }
    return this.http.put(`${this.apiUrl}/products/${productId}/change_state`, body);
  }

  // Violation reports
  getViolationReviews(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/reviews/violations`);
  }

  handleViolation(reviewId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/reviews/${reviewId}/violation`, {});
  }

  // Processing history
  getProcessingHistory(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/processing-history`);
  }

  // Seller appeals
  getSellerAppeals(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/seller-appeals`);
  }

  reviewSellerAppeal(appealId: number, decision: 'approve' | 'reject', notes: string): Observable<any> {
    const body = { decision, notes };
    return this.http.put(`${this.apiUrl}/seller-appeals/${appealId}/review`, body);
  }

  // User management
  banUser(userId: number, reason: string): Observable<any> {
    const body: UserBanRequest = { reason };
    return this.http.post(`${this.apiUrl}/users/${userId}/ban`, body);
  }

  unbanUser(userId: number, reason: string): Observable<any> {
    const body: UserBanRequest = { reason };
    return this.http.post(`${this.apiUrl}/users/${userId}/unban`, body);
  }

  getUser(userId: number): Observable<any> {
    return this.http.get<any>(`${environment.apiUrl}/users/${userId}`);
  }

  // Logs
  getViolationLogs(userId?: number): Observable<any[]> {
    let params = new HttpParams();
    if (userId) {
      params = params.set('user_id', userId.toString());
    }
    return this.http.get<any[]>(`${this.apiUrl}/violation-logs`, { params });
  }
}