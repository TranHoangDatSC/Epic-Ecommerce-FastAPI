import { Component } from '@angular/core';

@Component({
  selector: 'app-category-manage',
  standalone: true,
  imports: [],
  template: `
    <div class="container mt-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Category Management</h2>
        <button class="btn btn-primary">Add New Category</button>
      </div>
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Products Count</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td>Electronics</td>
                  <td>Electronic devices and accessories</td>
                  <td>25</td>
                  <td><span class="badge bg-success">Active</span></td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-1">Edit</button>
                    <button class="btn btn-sm btn-outline-danger">Delete</button>
                  </td>
                </tr>
                <tr>
                  <td>2</td>
                  <td>Clothing</td>
                  <td>Fashion and apparel</td>
                  <td>18</td>
                  <td><span class="badge bg-success">Active</span></td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-1">Edit</button>
                    <button class="btn btn-sm btn-outline-danger">Delete</button>
                  </td>
                </tr>
                <tr>
                  <td>3</td>
                  <td>Books</td>
                  <td>Books and publications</td>
                  <td>0</td>
                  <td><span class="badge bg-secondary">Inactive</span></td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-1">Edit</button>
                    <button class="btn btn-sm btn-outline-success me-1">Activate</button>
                    <button class="btn btn-sm btn-outline-danger">Delete</button>
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
export class CategoryManageComponent {}
