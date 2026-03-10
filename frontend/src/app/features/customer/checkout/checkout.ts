import { Component } from '@angular/core';

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [],
  template: `
    <div class="container mt-4">
      <h2>Checkout</h2>
      <div class="row">
        <div class="col-md-8">
          <div class="card mb-4">
            <div class="card-header">
              <h5>Shipping Information</h5>
            </div>
            <div class="card-body">
              <form>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="firstName" class="form-label">First Name</label>
                    <input type="text" class="form-control" id="firstName">
                  </div>
                  <div class="col-md-6 mb-3">
                    <label for="lastName" class="form-label">Last Name</label>
                    <input type="text" class="form-control" id="lastName">
                  </div>
                </div>
                <div class="mb-3">
                  <label for="address" class="form-label">Address</label>
                  <input type="text" class="form-control" id="address">
                </div>
                <div class="row">
                  <div class="col-md-4 mb-3">
                    <label for="city" class="form-label">City</label>
                    <input type="text" class="form-control" id="city">
                  </div>
                  <div class="col-md-4 mb-3">
                    <label for="state" class="form-label">State</label>
                    <input type="text" class="form-control" id="state">
                  </div>
                  <div class="col-md-4 mb-3">
                    <label for="zip" class="form-label">ZIP Code</label>
                    <input type="text" class="form-control" id="zip">
                  </div>
                </div>
              </form>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <h5>Payment Information</h5>
            </div>
            <div class="card-body">
              <form>
                <div class="mb-3">
                  <label for="cardNumber" class="form-label">Card Number</label>
                  <input type="text" class="form-control" id="cardNumber">
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="expiry" class="form-label">Expiry Date</label>
                    <input type="text" class="form-control" id="expiry" placeholder="MM/YY">
                  </div>
                  <div class="col-md-6 mb-3">
                    <label for="cvv" class="form-label">CVV</label>
                    <input type="text" class="form-control" id="cvv">
                  </div>
                </div>
              </form>
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
              <div class="d-flex justify-content-between">
                <span>Tax:</span>
                <span>$8.00</span>
              </div>
              <hr>
              <div class="d-flex justify-content-between fw-bold">
                <span>Total:</span>
                <span>$117.99</span>
              </div>
              <button class="btn btn-primary w-100 mt-3">Place Order</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class CheckoutComponent {}
