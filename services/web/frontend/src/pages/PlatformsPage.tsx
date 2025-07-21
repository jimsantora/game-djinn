export function PlatformsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Platforms</h1>
        <p className="text-gray-600">Manage gaming platform integrations</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Steam</h3>
          <p className="text-sm text-gray-600 mb-4">PC Gaming Platform</p>
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Available
            </span>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
              Configure
            </button>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Xbox Game Pass</h3>
          <p className="text-sm text-gray-600 mb-4">Microsoft Gaming</p>
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Available
            </span>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
              Configure
            </button>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">PlayStation Network</h3>
          <p className="text-sm text-gray-600 mb-4">Sony Gaming Platform</p>
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              Coming Soon
            </span>
            <button disabled className="text-gray-400 text-sm font-medium">
              Configure
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}