package main

import (
	"fmt"
	"image"
	"strings"

	"github.com/charmbracelet/lipgloss"
	"github.com/dolmen-go/kittyimg"
)

// Style definitions
var (
	// Outer application border
	outerBorderStyle = lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("240")).
		Padding(1)

	// Inner viewer border
	viewerBorderStyle = lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("240"))

	// Menu item styles
	menuItemStyle = lipgloss.NewStyle().
		PaddingLeft(2).
		PaddingRight(2)

	selectedMenuItemStyle = lipgloss.NewStyle().
		PaddingLeft(2).
		PaddingRight(2).
		Background(lipgloss.Color("18")).
		Foreground(lipgloss.Color("15"))

	// Placeholder text style
	placeholderStyle = lipgloss.NewStyle().
		Foreground(lipgloss.Color("240")).
		Align(lipgloss.Center)
)

// renderView renders the complete UI
func renderView(m *Model) string {
	// Add small margins to prevent edge clipping without borders
	innerWidth := m.termWidth - 4   // Small margin for edge safety
	innerHeight := m.termHeight - 2 // Small margin for edge safety

	// Split into viewer and menu - fixed menu height
	menuHeight := 3 // Fixed height for menu
	if innerHeight < 20 { // For very small terminals, use percentage
		menuHeight = int(float64(innerHeight) * 0.1)
		if menuHeight < 2 {
			menuHeight = 2
		}
	}
	viewerHeight := innerHeight - menuHeight

	// Render viewer pane
	viewerContent := renderViewerPane(m, innerWidth, viewerHeight)
	
	// Render menu pane
	menuContent := renderMenuPane(m, innerWidth, menuHeight)

	// Combine panes - no outer border
	return viewerContent + "\n" + menuContent
}

// renderViewerPane renders the image viewer pane
func renderViewerPane(m *Model, width, height int) string {
	// Add small margins to keep image away from screen edges
	contentWidth := width - 6   // Add margin to prevent edge clipping
	contentHeight := height - 4 // Add margin to prevent edge clipping

	// Get current image
	currentImage := m.getCurrentImage()
	if currentImage == "" {
		placeholder := placeholderStyle.
			Width(contentWidth).
			Height(contentHeight).
			Render("No images available")
		return viewerBorderStyle.
			Width(width).
			Height(height).
			Render(placeholder)
	}

	// Render the actual image
	imageContent := renderImageContent(m, currentImage, contentWidth, contentHeight)

	return viewerBorderStyle.
		Width(width).
		Height(height).
		Render(imageContent)
}

// renderImagePlaceholder renders a placeholder for the image
func renderImagePlaceholder(imagePath string, width, height int) string {
	// For now, just show the image path centered
	content := fmt.Sprintf("Image: %s\n\n[Image will be rendered here using Kitty graphics protocol]", imagePath)
	
	return placeholderStyle.
		Width(width).
		Height(height).
		Render(content)
}

// renderImageContent renders the actual image content
func renderImageContent(m *Model, imagePath string, width, height int) string {
	// Load the original image to get its dimensions
	img, err := loadImage(imagePath)
	if err != nil {
		// Fall back to placeholder on error
		errorContent := fmt.Sprintf("Error loading image: %s\n\n%v", imagePath, err)
		return placeholderStyle.
			Width(width).
			Height(height).
			Render(errorContent)
	}

	// Calculate optimal size respecting aspect ratio
	bounds := img.Bounds()
	originalWidth := float64(bounds.Dx())
	originalHeight := float64(bounds.Dy())
	imageAspectRatio := originalWidth / originalHeight
	
	// Terminal character cells are not square! Adjust for your specific terminal
	// Fine-tune character height to eliminate vertical stretching
	charWidth := 14.0  // pixels  
	charHeight := 26.0 // pixels (fine-tuning to reduce vertical stretch further)
	charAspectRatio := charWidth / charHeight // ~0.538
	
	// To compensate for narrow characters, we need to DIVIDE by the char aspect ratio
	// This will make us use more columns (wider) to achieve the correct image proportions
	adjustedAspectRatio := imageAspectRatio / charAspectRatio
	
	// Use 98% of viewer pane - back to larger size since we have margins now
	maxWidthChars := int(float64(width) * 0.98)
	maxHeightChars := int(float64(height) * 0.98)
	
	// Calculate actual size based on adjusted aspect ratio constraints
	var targetWidthChars, targetHeightChars int
	
	// Compare available space ratio with our adjusted aspect ratio
	availableRatio := float64(maxWidthChars) / float64(maxHeightChars)
	
	if availableRatio > adjustedAspectRatio {
		// Height is the limiting factor
		targetHeightChars = maxHeightChars
		targetWidthChars = int(float64(targetHeightChars) * adjustedAspectRatio)
	} else {
		// Width is the limiting factor
		targetWidthChars = maxWidthChars
		targetHeightChars = int(float64(targetWidthChars) / adjustedAspectRatio)
	}

	// Create Kitty graphics output with proper sizing and centering
	kittyOutput, err := renderImageToKittyWithSizeAndCenter(img, targetWidthChars, targetHeightChars, width, height)
	if err != nil {
		// Fall back to placeholder on error
		errorContent := fmt.Sprintf("Error rendering image: %s\n\n%v", imagePath, err)
		return placeholderStyle.
			Width(width).
			Height(height).
			Render(errorContent)
	}

	// Return the kitty graphics output
	return kittyOutput
}

// renderImageToKittyWithSizeAndCenter renders an image with sizing and centering
func renderImageToKittyWithSizeAndCenter(img image.Image, widthChars, heightChars, viewerWidth, viewerHeight int) (string, error) {
	// Calculate centering offsets - add back the margin we subtracted in renderViewerPane
	xOffsetChars := (viewerWidth - widthChars) / 2 + 3  // +3 to account for the -6 margin
	yOffsetChars := (viewerHeight - heightChars) / 2 + 2  // +2 to account for the -4 margin
	
	// Convert character offsets to pixel offsets (approximate)
	// Increase offsets to pull image away from screen edges
	xOffsetPixels := 24 // Larger offset to avoid edge clipping
	yOffsetPixels := 24 // Larger offset to avoid edge clipping
	
	// Use the basic kittyimg output and modify it
	var buf strings.Builder
	err := kittyimg.Fprint(&buf, img)
	if err != nil {
		return "", fmt.Errorf("failed to encode Kitty graphics: %w", err)
	}
	
	output := buf.String()
	
	// Add positioning and sizing parameters
	if strings.Contains(output, "a=T") {
		// Replace with our enhanced parameters including positioning
		newParams := fmt.Sprintf("a=T,c=%d,r=%d,X=%d,Y=%d,C=1,", widthChars, heightChars, xOffsetPixels, yOffsetPixels)
		output = strings.Replace(output, "a=T,", newParams, 1)
	}
	
	// Add padding for centering
	var result strings.Builder
	
	// Add vertical padding before image
	for i := 0; i < yOffsetChars; i++ {
		result.WriteString("\n")
	}
	
	// Add horizontal padding before image
	padding := strings.Repeat(" ", xOffsetChars)
	result.WriteString(padding + output)
	
	return result.String(), nil
}

// renderImageToKittyWithSize renders an image using Kitty graphics protocol with positioning and sizing (legacy)
func renderImageToKittyWithSize(img image.Image, widthChars, heightChars int) (string, error) {
	// Legacy function - use the new centering one with no centering
	return renderImageToKittyWithSizeAndCenter(img, widthChars, heightChars, widthChars, heightChars)
}

// renderImageToKitty renders an image using Kitty graphics protocol with positioning (legacy)
func renderImageToKitty(img image.Image) (string, error) {
	// Legacy function - use the new one with default sizing
	return renderImageToKittyWithSize(img, 0, 0)
}


// renderMenuPane renders the horizontal menu pane
func renderMenuPane(m *Model, width, height int) string {
	menuItems := m.getMenuItems()
	
	// Build menu string
	var menuParts []string
	for _, item := range menuItems {
		var rendered string
		if item.Selected {
			rendered = selectedMenuItemStyle.Render(item.Text)
		} else {
			rendered = menuItemStyle.Render(item.Text)
		}
		menuParts = append(menuParts, rendered)
	}

	menuString := strings.Join(menuParts, "")
	
	// Center the menu horizontally
	menuStyle := lipgloss.NewStyle().
		Width(width).
		Height(height).
		Align(lipgloss.Center).
		AlignVertical(lipgloss.Center)

	return menuStyle.Render(menuString)
}