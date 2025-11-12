import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

/**
 * A simple Swing application that demonstrates basic GUI components and event handling.
 * This application displays a "Hello World!" label and a button that changes the label text when clicked.
 * 
 * NODAL POINT BREAKDOWN:
 * 
 * 1. Java Fundamentals
 *    - Classes, methods, and object instantiation
 *    - Variable declaration and initialization
 *    - Access modifiers and encapsulation
 * 
 * 2. Swing Introduction
 *    - javax.swing package components
 *    - Event-driven programming paradigm
 *    - GUI lifecycle management
 * 
 * 3. JFrame Configuration
 *    - Window creation and properties
 *    - Layout management
 *    - Basic window operations
 * 
 * 4. Basic Components
 *    - JLabel for text display
 *    - JButton for user interaction
 *    - Component positioning and styling
 * 
 * 5. Event Management
 *    - ActionListener interface implementation
 *    - Event handling methods
 *    - Component-event binding
 * 
 * 6. Complete Application
 *    - Component integration
 *    - Application lifecycle
 *    - Execution and testing
 */
public class HelloWorldSwing extends JFrame implements ActionListener {
    
    // Component declarations
    private JLabel messageLabel;
    private JButton clickButton;
    
    /**
     * Constructor - Initializes the GUI components and configures the main frame
     * 
     * SUBTASKS EXECUTED:
     * - Create JFrame container
     * - Set window properties (title, size, close operation)
     * - Configure layout manager
     * - Initialize and position components
     * - Register event listeners
     */
    public HelloWorldSwing() {
        // Configure the main application window
        configureMainFrame();
        
        // Initialize and add GUI components
        initializeComponents();
    }
    
    /**
     * Configures the main JFrame properties
     * 
     * STEP-BY-STEP:
     * 1. Set window title
     * 2. Define window dimensions
     * 3. Specify close operation behavior
     * 4. Choose layout manager for component arrangement
     */
    private void configureMainFrame() {
        setTitle("Hello Cruel World Swing Application");
        setSize(350, 250);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new FlowLayout()); // Using FlowLayout for better component management
        setLocationRelativeTo(null); // Center the window on screen
    }
    
    /**
     * Creates and arranges all GUI components
     * 
     * STEP-BY-STEP:
     * 1. Create JLabel with initial text
     * 2. Create JButton with descriptive text
     * 3. Add components to the frame
     * 4. Register event listener for the button
     */
    private void initializeComponents() {
        // Create and configure the message label
        messageLabel = new JLabel("Hello Cruel World!");
        messageLabel.setFont(new Font("Arial", Font.BOLD, 16));
        messageLabel.setHorizontalAlignment(SwingConstants.CENTER);
        add(messageLabel);
        
        // Create and configure the interactive button
        clickButton = new JButton("Click Me!");
        clickButton.setFont(new Font("Arial", Font.PLAIN, 14));
        clickButton.addActionListener(this); // Register this class as action listener
        add(clickButton);
    }
    
    /**
     * Event handler method - Called when button is clicked
     * 
     * STEP-BY-STEP:
     * 1. Check event source
     * 2. Update label text
     * 3. Provide user feedback
     * 
     * @param actionEvent The event object containing action details
     */
    @Override
    public void actionPerformed(ActionEvent actionEvent) {
        // Verify the event source is our button
        if (actionEvent.getSource() == clickButton) {
            messageLabel.setText("Button Clicked! Hello Cruel Swing!");
        }
    }
    
    /**
     * Main method - Application entry point
     * 
     * STEP-BY-STEP:
     * 1. Create application instance
     * 2. Make frame visible
     * 3. Start event dispatch thread (implicitly)
     * 
     * @param args Command line arguments (not used)
     */
    public static void main(String[] args) {
        // Ensure GUI creation happens on Event Dispatch Thread
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                HelloWorldSwing helloWorldApp = new HelloWorldSwing();
                helloWorldApp.setVisible(true);
            }
        });
    }
}
