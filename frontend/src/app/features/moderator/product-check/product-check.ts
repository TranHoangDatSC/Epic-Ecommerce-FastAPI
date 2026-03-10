import { Component } from '@angular/core';

@Component({
  selector: 'app-product-check',
  standalone: true,
  imports: [],
  template: `
    <div class="container mt-4">
      <h2>Product Moderation</h2>
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>Image</th>
                  <th>Name</th>
                  <th>Seller</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><img src="https://via.placeholder.com/50" class="img-thumbnail" alt="Product"></td>
                  <td>Product A</td>
                  <td>John Seller</td>
                  <td>Electronics</td>
                  <td>$99.99</td>
                  <td><span class="badge bg-warning">Pending</span></td>
                  <td>
                    <button class="btn btn-sm btn-outline-success me-1">Approve</button>
                    <button class="btn btn-sm btn-outline-danger me-1">Reject</button>
                    <button class="btn btn-sm btn-outline-info">View Details</button>
                  </td>
                </tr>
                <tr>
                  <td><img src="https://via.placeholder.com/50" class="img-thumbnail" alt="Product"></td>
                  <td>Product B</td>
                  <td>Jane Seller</td>
                  <td>Clothing</td>
                  <td>$49.99</td>
                  <td><span class="badge bg-danger">Rejected</span></td>
                  <td>
                    <button class="btn btn-sm btn-outline-success me-1">Approve</button>
                    <button class="btn btn-sm btn-outline-warning me-1">Edit</button>
                    <button class="btn btn-sm btn-outline-info">View Details</button>
                  </td>
                </tr>
                <tr>
                  <td><img src="https://via.placeholder.com/50" class="img-thumbnail" alt="Product"></td>
                  <td>Product C</td>
                  <td>Bob Seller</td>
                  <td>Books</td>
                  <td>$19.99</td>
                  <td><span class="badge bg-success">Approved</span></td>
                  <td>
                    <button class="btn btn-sm btn-outline-info">View Details</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class ProductCheckComponent {}
