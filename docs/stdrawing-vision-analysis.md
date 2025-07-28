# Technical Drawing Analysis (stdrawing.py)

## Overview

The Technical Drawing Analysis application provides advanced AI-powered image analysis capabilities for engineering drawings, architectural plans, and technical documentation. Using Azure OpenAI's vision models (GPT-4.1 Vision and O3), this Streamlit application can interpret, analyze, and extract structured data from complex technical drawings.

## Features

### 🔍 Advanced Vision Analysis
- **Dual Model Support**: Choose between Azure GPT-4.1 Vision and O3 models
- **Technical Drawing Interpretation**: Specialized analysis for engineering and architectural drawings
- **Material Extraction**: Automated identification and listing of materials
- **Dimension Analysis**: Measurement and dimension extraction from drawings
- **Component Identification**: Recognition of technical components and symbols

### 📊 Structured Data Extraction
- **JSON Output**: Structured data extraction for integration with other systems
- **Materials List**: Comprehensive material identification and specifications
- **Quantity Calculations**: Automated quantity takeoffs and calculations
- **Technical Specifications**: Extraction of technical parameters and specifications
- **Custom Questions**: Interactive Q&A about uploaded drawings

### 🖼️ Multi-Format Support
- **Image Formats**: Support for JPG, JPEG, PNG image formats
- **High Resolution**: Processing of high-resolution technical drawings
- **Batch Processing**: Multiple image analysis capabilities
- **Quality Optimization**: Automatic image optimization for better analysis

## Technical Architecture

### Vision Models
- **Azure GPT-4.1 Vision**: Advanced vision capabilities for complex technical drawings
- **O3 Model**: Next-generation reasoning model for sophisticated analysis
- **Model Selection**: Dynamic switching between models based on analysis needs
- **API Integration**: Seamless integration with Azure OpenAI services

### Core Components
```python
# Vision Analysis Setup
def analyze_with_azure(image, question):
    # GPT-4.1 Vision analysis
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    )
    return response.choices[0].message.content

def analyze_with_o3(image, question):
    # O3 model analysis with advanced reasoning
    response = client.chat.completions.create(
        model="o3-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    )
    return response.choices[0].message.content
```

## Usage

### Quick Start
```bash
# Launch the Technical Drawing Analysis
streamlit run stdrawing.py
```

Access the application at: **http://localhost:8501**

### Analysis Process

#### 1. Image Upload
- **File Selection**: Upload JPG, JPEG, or PNG images
- **Preview**: Real-time preview of uploaded drawings
- **Quality Check**: Automatic validation of image quality and format
- **Multiple Uploads**: Support for analyzing multiple drawings

#### 2. Model Selection
- **GPT-4.1 Vision**: Best for general technical drawing analysis
- **O3 Model**: Advanced reasoning for complex engineering drawings
- **Comparison Mode**: Side-by-side analysis with both models
- **Performance Metrics**: Analysis time and accuracy tracking

#### 3. Question Configuration
- **Pre-defined Queries**: Common technical drawing questions
- **Custom Questions**: Specific analysis requirements
- **Analysis Scope**: Define scope of analysis (materials, dimensions, etc.)
- **Output Format**: Choose between text or structured JSON output

#### 4. Results Review
- **Analysis Results**: Comprehensive analysis results and insights
- **Structured Data**: JSON format for easy integration
- **Visual Annotations**: Highlighted areas and components
- **Export Options**: Save results in various formats

### Common Use Cases

#### Engineering Drawings
- **Component Analysis**: Identification of mechanical components
- **Assembly Instructions**: Understanding of assembly procedures
- **Tolerance Analysis**: Extraction of dimensional tolerances
- **Material Specifications**: Material type and grade identification

#### Architectural Plans
- **Space Analysis**: Room dimensions and layout analysis
- **Material Takeoffs**: Construction material quantity calculations
- **Code Compliance**: Building code compliance checking
- **Structural Elements**: Identification of structural components

#### Technical Schematics
- **Circuit Analysis**: Electronic circuit interpretation
- **Flow Diagrams**: Process flow understanding
- **P&ID Analysis**: Piping and instrumentation diagram interpretation
- **Wiring Diagrams**: Electrical wiring analysis

## Configuration

### Environment Variables
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=<your_endpoint>
AZURE_OPENAI_KEY=<your_key>
AZURE_OPENAI_DEPLOYMENT=<your_deployment>

# Model Deployments
GPT4_VISION_DEPLOYMENT=<gpt4_vision_deployment>
O3_MODEL_DEPLOYMENT=<o3_model_deployment>

# API Configuration
AZURE_API_VERSION=2024-06-01
```

### Model Configuration
```python
# Vision Model Settings
SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png']
MAX_IMAGE_SIZE = 20_000_000  # 20MB
IMAGE_QUALITY = 85  # JPEG quality for optimization

# Analysis Parameters
DEFAULT_QUESTIONS = [
    "Analyze this technical drawing and extract all materials, quantities, and dimensions",
    "Identify all components and their specifications",
    "Extract dimensional information and tolerances",
    "Provide a structured analysis in JSON format"
]
```

## Advanced Features

### Structured Data Extraction
```json
{
    "drawing_type": "mechanical_assembly",
    "components": [
        {
            "name": "Bearing",
            "type": "Ball Bearing",
            "specifications": "6205-2RS",
            "quantity": 2,
            "location": "Shaft Assembly"
        }
    ],
    "materials": [
        {
            "type": "Steel",
            "grade": "AISI 1045",
            "quantity": "1 piece",
            "application": "Main Shaft"
        }
    ],
    "dimensions": [
        {
            "feature": "Overall Length",
            "value": "150mm",
            "tolerance": "±0.1mm"
        }
    ]
}
```

### Batch Processing
- **Multiple Images**: Process multiple drawings simultaneously
- **Comparative Analysis**: Compare different versions of drawings
- **Assembly Analysis**: Analyze complete assembly drawings
- **Progress Tracking**: Real-time progress for batch operations

### Quality Assurance
- **Confidence Scoring**: AI confidence levels for extracted data
- **Validation Checks**: Automated validation of extracted information
- **Error Detection**: Identification of potential analysis errors
- **Manual Review**: Human-in-the-loop validation capabilities

## Integration Capabilities

### CAD System Integration
- **AutoCAD**: Integration with AutoCAD drawing files
- **SolidWorks**: SolidWorks drawing analysis
- **Revit**: Architectural drawing analysis
- **Generic CAD**: Support for various CAD formats

### Data Export Options
- **JSON Format**: Structured data for system integration
- **CSV Export**: Tabular data export for spreadsheet analysis
- **PDF Reports**: Comprehensive analysis reports
- **XML Format**: Structured markup for enterprise systems

### API Integration
- **REST API**: RESTful API for system integration
- **Webhook Support**: Real-time notifications and updates
- **Batch API**: Bulk processing capabilities
- **Authentication**: Secure API access and authorization

## Performance Optimization

### Image Processing
- **Resolution Optimization**: Automatic image resolution adjustment
- **Compression**: Intelligent image compression for faster processing
- **Format Conversion**: Automatic format conversion for optimal analysis
- **Quality Enhancement**: Image quality improvement for better analysis

### Model Performance
- **Caching**: Intelligent caching of analysis results
- **Load Balancing**: Distributed processing for high availability
- **Rate Limiting**: Optimal API usage and rate management
- **Error Handling**: Robust error handling and recovery

## Use Cases by Industry

### Manufacturing
- **Production Drawings**: Analysis of manufacturing drawings and specifications
- **Quality Control**: Automated quality control based on drawing specifications
- **Bill of Materials**: Automated BOM generation from drawings
- **Process Planning**: Manufacturing process planning assistance

### Construction
- **Blueprint Analysis**: Comprehensive building plan analysis
- **Material Estimation**: Accurate material quantity estimation
- **Code Compliance**: Building code compliance verification
- **Project Planning**: Construction project planning assistance

### Engineering Services
- **Design Review**: Automated design review and validation
- **Documentation**: Technical documentation generation
- **Compliance Checking**: Regulatory compliance verification
- **Cost Estimation**: Project cost estimation based on drawings

### Architecture
- **Space Planning**: Architectural space analysis and planning
- **Design Validation**: Design concept validation and review
- **Material Selection**: Material selection and specification
- **Visualization**: Enhanced visualization and presentation

## Best Practices

### Image Preparation
1. **High Resolution**: Use high-resolution images for better analysis
2. **Clear Quality**: Ensure drawings are clear and legible
3. **Proper Lighting**: Avoid shadows and glare in scanned drawings
4. **Format Selection**: Use appropriate image formats (PNG for line drawings)

### Analysis Optimization
1. **Specific Questions**: Ask specific, focused questions for better results
2. **Model Selection**: Choose the appropriate model for the drawing type
3. **Context Provision**: Provide context about the drawing type and purpose
4. **Result Validation**: Always validate AI results against known standards

### Quality Assurance
1. **Human Review**: Implement human review for critical analyses
2. **Validation Checks**: Use multiple validation methods
3. **Error Reporting**: Implement comprehensive error reporting
4. **Continuous Improvement**: Regular model updates and improvements

## Troubleshooting

### Common Issues
- **Image Quality**: Poor image quality affecting analysis accuracy
- **Format Issues**: Unsupported image formats or corrupted files
- **Model Errors**: API errors or model deployment issues
- **Performance Issues**: Slow analysis or timeout problems

### Solutions
- **Image Enhancement**: Use image enhancement tools before analysis
- **Format Conversion**: Convert images to supported formats
- **Error Handling**: Implement robust error handling and retry logic
- **Performance Tuning**: Optimize image size and analysis parameters

## Future Enhancements

### Planned Features
- **3D Model Analysis**: Support for 3D model analysis and interpretation
- **Video Processing**: Analysis of technical video content
- **Augmented Reality**: AR overlays for real-world drawing validation
- **Machine Learning**: Custom ML models for specific drawing types

### Integration Roadmap
- **PLM Integration**: Product lifecycle management system integration
- **ERP Integration**: Enterprise resource planning system connections
- **Cloud Storage**: Direct integration with cloud storage services
- **Mobile Apps**: Native mobile applications for field analysis

---

For more information about the AgenticAI Foundry platform, see the [main documentation](../README.md).