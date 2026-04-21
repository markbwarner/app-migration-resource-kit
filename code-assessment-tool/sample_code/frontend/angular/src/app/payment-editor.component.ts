import { HttpClient } from "@angular/common/http";
import { Component } from "@angular/core";

@Component({
  selector: "app-payment-editor",
  template: `
    <h2>Payment Editor</h2>
    <form>
      <label>Card Number</label>
      <input [(ngModel)]="cardNumber" name="cardNumber" />
      <label>CVV</label>
      <input [(ngModel)]="cvv" name="cvv" />
      <label>Billing Address</label>
      <input [(ngModel)]="billingAddress" name="billingAddress" />
      <button type="button" (click)="submitPayment()">Submit</button>
    </form>
  `,
})
export class PaymentEditorComponent {
  cardNumber = "4111111111111111";
  cvv = "123";
  billingAddress = "101 Main Street";
  emailAddress = "customer@example.com";

  constructor(private http: HttpClient) {}

  submitPayment(): void {
    this.http
      .post("/payments/api/authorize", {
        cardNumber: this.cardNumber,
        cvv: this.cvv,
        billingAddress: this.billingAddress,
        emailAddress: this.emailAddress,
      })
      .subscribe();
  }
}
