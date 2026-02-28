export default function InvalidProductCard({ item }) {
  return (
    <div className="bg-red-50 rounded-2xl border border-red-200 p-5">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-red-700 font-semibold">Invalid Product</span>
      </div>

      <p className="text-sm font-medium text-neutral-800 mb-1">
        {item?.name || 'Unknown Product'}
      </p>

      {item?.url && (
        <p className="text-xs text-neutral-500 break-all mb-2">
          {item.url}
        </p>
      )}

      <p className="text-sm text-red-700">
        {item?.reason || 'This link is not a headphone-related product.'}
      </p>
    </div>
  )
}
