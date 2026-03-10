import { Component } from '@angular/core';

@Component({
  selector: 'app-user-manage',
  standalone: true,
  imports: [],
  template: `
    <div class="container mt-4">
      <h2>User Management</h2>
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td>John Doe</td>
                  <td>john@example.com</td>
                  <td><span class="badge bg-primary">Customer</span></td>
                  <td><span class="badge bg-success">Active</span></td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-1">Edit</button>
                    <button class="btn btn-sm btn-outline-warning me-1">Suspend</button>
                    <button class="btn btn-sm btn-outline-danger">Delete</button>
                  </td>
                </tr>
                <tr>
                  <td>2</td>
                  <td>Jane Smith</td>
                  <td>jane@example.com</td>
                  <td><span class="badge bg-info">Seller</span></td>
                  <td><span class="badge bg-success">Active</span></td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-1">Edit</button>
                    <button class="btn btn-sm btn-outline-warning me-1">Suspend</button>
                    <button class="btn btn-sm btn-outline-danger">Delete</button>
                  </td>
                </tr>
                <tr>
                  <td>3</td>
                  <td>Bob Johnson</td>
                  <td>bob@example.com</td>
                  <td><span class="badge bg-secondary">Moderator</span></td>
                  <td><span class="badge bg-warning">Suspended</span></td>
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
export class UserManageComponent {}
