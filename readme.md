### Project Description: AI-Powered Frontend Code Generator

This project leverages the **Gemini model** to automate the generation of frontend code (HTML, CSS, and JavaScript) based on design inputs, including images of UI mockups such as those from **Figma**. The system transforms these designs into responsive and functional web pages, offering developers the ability to further refine and synchronize code directly from a **VS Code extension**.

#### Key Features:

1. **AI-Generated Frontend Code**:

   - The project uses the **Gemini model** to convert design images (e.g., Figma screenshots) into fully functional web pages with HTML, CSS, and JavaScript code.
   - Supports multiple pages connected together, allowing the creation of complete multi-page web applications.

2. **VS Code Extension Integration**:

   - A **Sync Code** command allows users to synchronize the generated code for the app with VS Code environment. Any updates or changes to the prompt result in updates to the codebase.

3. **Customizable Code Generation**:

   - Developers can either fully customize the **prompt** to generate a unique UI and functionality or use predefined parameters for quick and effectivve generation for the page.
   - Generated code can be manually modified, allowing developers to maintain full control over customization.

4. **App Preview & Deployment**:

   - An API endpoint for **preview window** allows users to see how the generated code will look in a browser, simulating real-time changes during development.
   - Supports the generation of not just static content, but also functional JavaScript for handling UI interactions.

5. **End-to-End Application Support**:
   - Facilitates the generation of entire applications, including multi-page navigation, dynamic content rendering, and handling user input and interactions.

---

The **core functionality** of this project is to take a **design image** as input, transform it into code, and provide seamless **synchronization** and updates through VS Code, allowing for a flexible and efficient development workflow
