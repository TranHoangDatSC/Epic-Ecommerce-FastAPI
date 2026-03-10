import { Component } from '@angular/core';

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [],
  template: `
    <div class="container mt-4">
      <h2>Shopping Cart</h2>
      <div class="row">
        <div class="col-md-8">
          <div class="card mb-3">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-2">
                  <img src="https://via.placeholder.com/100" class="img-fluid" alt="Product">
                </div>
                <div class="col-md-4">
                  <h5>Product Name</h5>
                  <p class="text-muted">Category</p>
                </div>
                <div class="col-md-2">
                  <div class="input-group">
                    <button class="btn btn-outline-secondary btn-sm">-</button>
                    <input type="number" class="form-control form-control-sm text-center" value="1" min="1">
                    <button class="btn btn-outline-secondary btn-sm">+</button>
                  </div>
                </div>
                <div class="col-md-2">
                  <span class="fw-bold">$99.99</span>
                </div>
                <div class="col-md-2">
                  <button class="btn btn-danger btn-sm">Remove</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-body">
              <h5>Order Summary</h5>
              <hr>
              <div class="d-flex justify-content-between">
                <span>Subtotal:</span>
                <span>$99.99</span>
              </div>
              <div class="d-flex justify-content-between">
                <span>Shipping:</span>
                <span>$10.00</span>
              </div>
              <hr>
              <div class="d-flex justify-content-between fw-bold">
                <span>Total:</span>
                <span>$109.99</span>
              </div>
              <button class="btn btn-primary w-100 mt-3">Proceed to Checkout</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class CartComponent {}
