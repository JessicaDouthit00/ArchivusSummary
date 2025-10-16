import React, { useState } from 'react';
import { Upload, FileSpreadsheet, Image, Download, X, CheckCircle, Loader2, AlertCircle, Sparkles } from 'lucide-react';

export default function HandwritingConverter() {
  const [step, setStep] = useState(1);
  const [template, setTemplate] = useState(null);
  const [images, setImages] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleTemplateUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setTemplate(file);
    }
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    const validImages = files.filter(f => f.type.startsWith('image/'));
    
    if (images.length + validImages.length > 100) {
      alert('Maximum 100 images allowed');
      return;
    }
    
    const newImages = validImages.map((file, idx) => ({
      id: Date.now() + idx,
      file,
      name: file.name,
      preview: URL.createObjectURL(file),
      status: 'pending'
    }));
    
    setImages([...images, ...newImages]);
  };

  const removeImage = (id) => {
    setImages(images.filter(img => img.id !== id));
  };

  const processImages = async () => {
    setProcessing(true);
    setStep(3);
    
    for (let i = 0; i < images.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setImages(prev => prev.map((img, idx) => 
        idx === i ? { ...img, status: 'completed' } : img
      ));
      
      setUploadProgress(((i + 1) / images.length) * 100);
      
      setResults(prev => [...prev, {
        imageName: images[i].name,
        rowsExtracted: Math.floor(Math.random() * 20) + 5,
        confidence: (85 + Math.random() * 14).toFixed(1)
      }]);
    }
    
    setProcessing(false);
  };

  const downloadResults = () => {
    alert('Excel file download would start here. In production, this would generate and download the compiled spreadsheet.');
  };

  const reset = () => {
    setStep(1);
    setTemplate(null);
    setImages([]);
    setResults([]);
    setUploadProgress(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <FileSpreadsheet className="w-16 h-16 text-cyan-400" />
              <Sparkles className="w-6 h-6 text-yellow-400 absolute -top-2 -right-2 animate-pulse" />
            </div>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent mb-4">
            Handwriting to Spreadsheet
          </h1>
          <p className="text-cyan-100/80 text-lg">
            Convert handwritten research data to Excel spreadsheets with AI precision
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-16">
          {[1, 2, 3].map((s) => (
            <React.Fragment key={s}>
              <div className="flex items-center">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 ${
                  step >= s 
                    ? 'bg-gradient-to-br from-cyan-400 to-blue-500 text-white shadow-lg shadow-cyan-500/50' 
                    : 'bg-slate-800/50 text-slate-500 border-2 border-slate-700'
                }`}>
                  {s}
                </div>
                <span className={`ml-3 font-semibold transition-colors ${
                  step >= s ? 'text-cyan-300' : 'text-slate-500'
                }`}>
                  {s === 1 ? 'Template' : s === 2 ? 'Upload Images' : 'Process'}
                </span>
              </div>
              {s < 3 && (
                <div className={`w-24 h-1 mx-4 rounded-full transition-all duration-300 ${
                  step > s ? 'bg-gradient-to-r from-cyan-400 to-blue-500' : 'bg-slate-700/50'
                }`} />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Step 1: Template Upload */}
        {step === 1 && (
          <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-700/50 p-10">
            <h2 className="text-3xl font-bold text-white mb-3">
              Step 1: Upload Template
            </h2>
            <p className="text-cyan-100/70 mb-8 text-lg">
              Upload your Excel template that defines the structure of your data table
            </p>
            
            <div className="border-2 border-dashed border-cyan-500/30 rounded-xl p-16 text-center hover:border-cyan-400/60 hover:bg-slate-700/20 transition-all duration-300 group">
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleTemplateUpload}
                className="hidden"
                id="template-upload"
              />
              <label htmlFor="template-upload" className="cursor-pointer">
                <div className="relative inline-block">
                  <FileSpreadsheet className="w-20 h-20 text-cyan-400/60 group-hover:text-cyan-400 transition-colors mx-auto mb-6" />
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-cyan-400 rounded-full animate-ping"></div>
                </div>
                <p className="text-xl font-semibold text-white mb-3">
                  Click to upload template
                </p>
                <p className="text-cyan-100/60">
                  Excel (.xlsx, .xls) or CSV files
                </p>
              </label>
            </div>

            {template && (
              <div className="mt-8 p-5 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 backdrop-blur rounded-xl flex items-center justify-between border border-emerald-500/30">
                <div className="flex items-center">
                  <div className="bg-emerald-500 rounded-full p-2 mr-4">
                    <CheckCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-white text-lg">{template.name}</p>
                    <p className="text-cyan-100/70">
                      {(template.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setTemplate(null)}
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/20 p-2 rounded-lg transition-all"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            )}

            <button
              onClick={() => setStep(2)}
              disabled={!template}
              className="w-full mt-10 bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:from-cyan-400 hover:to-blue-500 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-cyan-500/50 disabled:shadow-none"
            >
              Next: Upload Images →
            </button>
          </div>
        )}

        {/* Step 2: Image Upload */}
        {step === 2 && (
          <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-700/50 p-10">
            <h2 className="text-3xl font-bold text-white mb-3">
              Step 2: Upload Handwritten Images
            </h2>
            <p className="text-cyan-100/70 mb-8 text-lg">
              Upload up to 100 images of handwritten data (JPG, PNG, HEIC)
            </p>

            <div className="border-2 border-dashed border-cyan-500/30 rounded-xl p-16 text-center hover:border-cyan-400/60 hover:bg-slate-700/20 transition-all duration-300 mb-8 group">
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                <div className="relative inline-block">
                  <Image className="w-20 h-20 text-cyan-400/60 group-hover:text-cyan-400 transition-colors mx-auto mb-6" />
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-cyan-400 rounded-full animate-ping"></div>
                </div>
                <p className="text-xl font-semibold text-white mb-3">
                  Click to upload images
                </p>
                <p className="text-cyan-100/60">
                  <span className="text-cyan-400 font-bold text-2xl">{images.length}</span>
                  <span className="text-white/40 mx-2">/</span>
                  <span className="text-white/60">100 images uploaded</span>
                </p>
              </label>
            </div>

            {images.length > 0 && (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 max-h-96 overflow-y-auto p-2">
                  {images.map((img) => (
                    <div key={img.id} className="relative group">
                      <div className="relative rounded-lg overflow-hidden border-2 border-slate-700 hover:border-cyan-400 transition-all duration-300">
                        <img
                          src={img.preview}
                          alt={img.name}
                          className="w-full h-32 object-cover group-hover:scale-110 transition-transform duration-300"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                      </div>
                      <button
                        onClick={() => removeImage(img.id)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-all hover:bg-red-600 shadow-lg"
                      >
                        <X className="w-4 h-4" />
                      </button>
                      <p className="text-xs text-cyan-100/60 mt-2 truncate">
                        {img.name}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={() => setStep(1)}
                    className="flex-1 bg-slate-700/50 text-white py-4 px-8 rounded-xl font-bold text-lg hover:bg-slate-600/50 transition-all duration-300 border border-slate-600"
                  >
                    ← Back
                  </button>
                  <button
                    onClick={processImages}
                    disabled={images.length === 0}
                    className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:from-cyan-400 hover:to-blue-500 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-cyan-500/50 disabled:shadow-none"
                  >
                    Process Images →
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {/* Step 3: Processing & Results */}
        {step === 3 && (
          <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-700/50 p-10">
            <h2 className="text-3xl font-bold text-white mb-6">
              {processing ? (
                <span className="flex items-center">
                  <Loader2 className="w-8 h-8 mr-3 animate-spin text-cyan-400" />
                  Processing Images...
                </span>
              ) : (
                <span className="flex items-center">
                  <CheckCircle className="w-8 h-8 mr-3 text-emerald-400" />
                  Processing Complete!
                </span>
              )}
            </h2>

            {processing && (
              <div className="mb-10">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold text-cyan-100/80">
                    Progress
                  </span>
                  <span className="text-lg font-bold text-cyan-400">
                    {Math.round(uploadProgress)}%
                  </span>
                </div>
                <div className="w-full bg-slate-700/50 rounded-full h-4 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-cyan-500 to-blue-600 h-4 rounded-full transition-all duration-300 shadow-lg shadow-cyan-500/50"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            <div className="space-y-3 max-h-96 overflow-y-auto mb-8 p-2">
              {images.map((img) => (
                <div
                  key={img.id}
                  className="flex items-center justify-between p-4 bg-slate-700/30 rounded-xl border border-slate-600/50 hover:bg-slate-700/50 transition-all"
                >
                  <div className="flex items-center flex-1">
                    <img
                      src={img.preview}
                      alt={img.name}
                      className="w-14 h-14 object-cover rounded-lg mr-4 border-2 border-slate-600"
                    />
                    <span className="text-sm text-cyan-100/80 truncate font-medium">
                      {img.name}
                    </span>
                  </div>
                  {img.status === 'pending' && (
                    <Loader2 className="w-6 h-6 text-cyan-400 animate-spin" />
                  )}
                  {img.status === 'completed' && (
                    <div className="bg-emerald-500 rounded-full p-1">
                      <CheckCircle className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {!processing && results.length > 0 && (
              <>
                <div className="bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30 rounded-xl p-6 mb-8 backdrop-blur">
                  <div className="flex items-start">
                    <div className="bg-emerald-500 rounded-full p-2 mr-4">
                      <CheckCircle className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="font-bold text-white text-xl mb-2">
                        Successfully processed {results.length} images
                      </p>
                      <p className="text-cyan-100/70 text-lg">
                        Total rows extracted: <span className="text-cyan-400 font-bold">{results.reduce((sum, r) => sum + r.rowsExtracted, 0)}</span>
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={reset}
                    className="flex-1 bg-slate-700/50 text-white py-4 px-8 rounded-xl font-bold text-lg hover:bg-slate-600/50 transition-all duration-300 border border-slate-600"
                  >
                    Start New Conversion
                  </button>
                  <button
                    onClick={downloadResults}
                    className="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:from-emerald-400 hover:to-cyan-500 transition-all duration-300 shadow-lg hover:shadow-emerald-500/50 flex items-center justify-center"
                  >
                    <Download className="w-6 h-6 mr-3" />
                    Download Excel
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
