# AutoMove - Car Sales Application

AutoMove is a web application designed for selling cars, where dealers can list vehicles, and customers can browse, add cars to their cart, and purchase them online. The application includes features for generating invoices in PDF format, which are then automatically sent to the customer's email. The app is built using Django on the back-end and JavaScript on the front-end.

## Description

AutoMove allows car dealers to create, update, and delete car listings. Customers can add vehicles to their cart, and once they are ready to purchase, they can generate an invoice in PDF format, which will be sent to their email address. Additionally, the app ensures that only authorized users can access certain pages, such as creating or editing car listings.

## Features

- **Account Confirmation**: After registering, the user will receive an email to confirm the account.
- **Car Management**: Admins and authorized moderators can create, update, and delete car listings.
- **Car Search and Filtering**: Customers can search and filter cars based on various characteristics (price, make, model, year, etc.).
- **Shopping Cart**: Customers can add cars to their shopping cart, adjust quantities and remove items. It is implemented using JavaScript and  **localStorage**.
- **Invoice Generation**: After completing a purchase, the application generates an invoice in PDF format.
- **Email Notifications**: The generated invoice is automatically emailed to the customer.
- **Permissions System**: Only users with the appropriate permissions (admins or moderators) can create or manage car listings. If a user without proper permissions tries to access those pages, they are redirected to an error page with a message stating they don't have access.\
- **Task Scheduler**: The application uses a taskk scheduler for the following tasks:
  - Deleting unconfirmed accounts after 5 minute.
  - Checking the stock of each car, and if ny car's stock is below 2, an email is sent to the admin to request restocking.
  - A newsletter is sent every Thursday to users who have been registered for more than one hour.
  - The system checks for users whose last activity (last_login) was more then 6 days ago. These users will have their is_active flag set to False, effectively deactivating them.
