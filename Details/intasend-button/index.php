<?php
use IntaSend\IntaSendPHP\Checkout;
use IntaSend\IntaSendPHP\Customer;

$credentials = [
'publishable_key' =>  env('INTASEND_PUBLISHABLE_KEY'),
'test' =>  env('INTASEND_TEST_ENVIRONMENT', true),
];

$customer = new Customer();
$customer->first_name = "Joe";
$customer->last_name = "Doe";
$customer->email = "joe@doe.com";
$customer->country = "KE";

$amount = 10;
$currency = "KES";

// Add your website and redirect url where the user will be redirected on success
$host = "https://example.com";
$redirect_url = "https://example.com/callback";
$ref_order_number = "test-order-10";

$checkout = new Checkout();
$checkout->init($credentials);
$resp = $checkout->create($amount = $amount, $currency = $currency, $customer = $customer, $host=$host, $redirect_url = $redirect_url, $api_ref = $ref_order_number, $comment = null, $method = null);

// Redirect the user to the URL to complete payment
print_r($resp->url);
Send M-Pesa STK-Push
Checkout API generates a URL that enables you to do M-Pesa collection and other payment methods. In case you want to leverage only the M-Pesa STK-Push option, you might want to consider this the collection->mpesa_stk_push() option.

use IntaSend\IntaSendPHP\Collection;
$credentials = [
'publishable_key' =>  env('INTASEND_PUBLISHABLE_KEY'),
'test' =>  env('INTASEND_TEST_ENVIRONMENT', true),
];


$collection = new Collection();
$collection->init($credentials);

$response = $collection->create($amount=10, $phone_number="2547...", $currency="KES", $method="MPESA_STK_PUSH", $api_ref="Your API Ref", $name="", $email="john@example.com");
print_r($response);