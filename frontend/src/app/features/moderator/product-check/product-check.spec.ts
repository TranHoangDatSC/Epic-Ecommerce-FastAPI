import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProductCheckComponent } from './product-check';

describe('ProductCheckComponent', () => {
  let component: ProductCheckComponent;
  let fixture: ComponentFixture<ProductCheckComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProductCheckComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ProductCheckComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
