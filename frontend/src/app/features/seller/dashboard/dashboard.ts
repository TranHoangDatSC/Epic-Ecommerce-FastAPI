import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [],
  template: `
    <div class="container mt-4">
      <h2>Seller Dashboard</h2>
      <div class="row">
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h5 class="card-title">Total Sales</h5>
              <h3 class="text-primary">$12,345</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h5 class="card-title">Orders</h5>
              <h3 class="text-success">156</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h5 class="card-title">Products</h5>
              <h3 class="text-info">42</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h5 class="card-title">Reviews</h5>
              <h3 class="text-warning">89</h3>
            </div>
          </div>
        </div>
      </div>
      <div class="row mt-4">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5>Recent Orders</h5>
            </div>
            <div class="card-body">
              <div class="list-group">
                <div class="list-group-item">
                  <div class="d-flex justify-content-between">
                    <span>Order #12345</span>
                    <span class="badge bg-success">Completed</span>
                  </div>
                  <small class="text-muted">$99.99 - 2 days ago</small>
                </div>
                <div class="list-group-item">
                  <div class="d-flex justify-content-between">
                    <span>Order #12346</span>
                    <span class="badge bg-warning">Pending</span>
                  </div>
                  <small class="text-muted">$149.99 - 3 days ago</small>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5>Top Products</h5>
            </div>
            <div class="card-body">
              <div class="list-group">
                <div class="list-group-item d-flex justify-content-between align-items-center">
                  Product A
                  <span class="badge bg-primary rounded-pill">25 sales</span>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                  Product B
                  <span class="badge bg-primary rounded-pill">18 sales</span>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                  Product C
                  <span class="badge bg-primary rounded-pill">12 sales</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class DashboardComponent {}
