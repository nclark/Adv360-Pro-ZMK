package main

import (
	"fmt"
	"image"
	"os"

	"github.com/dolmen-go/kittyimg"
	"golang.org/x/image/draw"

	_ "image/jpeg"
	_ "image/png"
)

// loadImage loads an image from file
func loadImage(filepath string) (image.Image, error) {
	f, err := os.Open(filepath)
	if err != nil {
		return nil, fmt.Errorf("failed to open image file %s: %w", filepath, err)
	}
	defer f.Close()

	img, _, err := image.Decode(f)
	if err != nil {
		return nil, fmt.Errorf("failed to decode image file %s: %w", filepath, err)
	}

	return img, nil
}

// resizeImage resizes an image to fit within the given dimensions while preserving aspect ratio
func resizeImage(img image.Image, maxWidth, maxHeight int) image.Image {
	bounds := img.Bounds()
	origWidth := bounds.Dx()
	origHeight := bounds.Dy()

	// Calculate new dimensions while preserving aspect ratio
	var newWidth, newHeight int
	
	// Calculate scale factors
	scaleX := float64(maxWidth) / float64(origWidth)
	scaleY := float64(maxHeight) / float64(origHeight)
	
	// Use the smaller scale factor to ensure image fits within bounds
	scale := scaleX
	if scaleY < scaleX {
		scale = scaleY
	}
	
	newWidth = int(float64(origWidth)*scale + 0.5)   // Round to nearest integer
	newHeight = int(float64(origHeight)*scale + 0.5) // Round to nearest integer
	
	// Don't upscale images
	if scale > 1.0 {
		newWidth = origWidth
		newHeight = origHeight
	}

	// Create new image with calculated dimensions
	dst := image.NewRGBA(image.Rect(0, 0, newWidth, newHeight))

	// Use CatmullRom for high-quality scaling
	draw.CatmullRom.Scale(dst, dst.Bounds(), img, bounds, draw.Over, nil)

	return dst
}

// renderImageToTerminal renders an image to the terminal using Kitty graphics protocol
func renderImageToTerminal(img image.Image) (string, error) {
	// Use kittyimg to render the image
	// This will be integrated into the TUI later
	kittyimg.Fprintln(os.Stdout, img)
	return "[Kitty graphics rendered]", nil
}

// getImageForDisplay loads and resizes an image for display
func (m *Model) getImageForDisplay(filepath string, width, height int) (image.Image, error) {
	// Check if we have a cached resized image
	cacheKey := fmt.Sprintf("%s_%dx%d", filepath, width, height)
	if resized, exists := m.resizedImages[cacheKey]; exists {
		return resized, nil
	}

	// Check if we have the original image cached
	var img image.Image
	if cached, exists := m.images[filepath]; exists {
		img = cached
	} else {
		// Load the image
		var err error
		img, err = loadImage(filepath)
		if err != nil {
			return nil, err
		}
		// Cache the original image
		m.images[filepath] = img
	}

	// Resize the image
	resized := resizeImage(img, width, height)
	
	// Cache the resized image
	m.resizedImages[cacheKey] = resized

	return resized, nil
}