import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserManageComponent } from './user-manage';

describe('UserManageComponent', () => {
  let component: UserManageComponent;
  let fixture: ComponentFixture<UserManageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserManageComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(UserManageComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
