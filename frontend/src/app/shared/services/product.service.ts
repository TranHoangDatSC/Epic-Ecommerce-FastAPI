import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Product } from '../../core/models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = `${environment.apiUrl}/products`;

  constructor(private http: HttpClient) {}

  getProducts(params?: {
    skip?: number;
    limit?: number;
    category_id?: number;
    search?: string;
    sort_by?: string;
  }): Observable<Product[]> {
    let httpParams = new HttpParams();

    if (params) {
      if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
      if (params.category_id !== undefined) httpParams = httpParams.set('category_id', params.category_id.toString());
      if (params.search) httpParams = httpParams.set('search', params.search);
      if (params.sort_by) httpParams = httpParams.set('sort_by', params.sort_by);
    }

    return this.http.get<Product[]>(this.apiUrl, { params: httpParams });
  }

  getProduct(id: number): Observable<Product> {
    return this.http.get<Product>(`${this.apiUrl}/${id}`);
  }

  createProduct(formData: FormData): Observable<Product> {
    return this.http.post<Product>(this.apiUrl, formData);
  }

  updateProduct(id: number, product: Partial<Product>): Observable<Product> {
    return this.http.put<Product>(`${this.apiUrl}/${id}`, product);
  }

  deleteProduct(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  getMyProducts(params?: { skip?: number; limit?: number }): Observable<Product[]> {
    let httpParams = new HttpParams();
    if (params) {
      if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
    }

    return this.http.get<Product[]>(`${this.apiUrl}/seller/my-products`, { params: httpParams });
  }
}