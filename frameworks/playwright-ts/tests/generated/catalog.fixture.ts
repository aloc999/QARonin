/**
 * Catalog fixture: hand-maintained mirror of the seeded catalog in
 * `apps/demo-target/app/seed.py` (PRODUCTS, ids follow insertion order 1-8).
 * There is no seed.json; update this file together with seed.py.
 * Price strings follow the template filter `$%.2f` in
 * `apps/demo-target/app/templates/products.html`.
 */
export interface CatalogProduct {
  id: number;
  name: string;
  description: string;
  price: number;
  priceText: string;
  /**
   * Raw `data-price` attribute value. Jinja renders the Python float
   * (`str(74.0) == "74.0"`), while JS `String(74.0) == "74"` — so this
   * cannot be derived with String(); it is pinned explicitly per product.
   */
  dataPrice: string;
}

export const CATALOG: CatalogProduct[] = [
  { id: 1, name: "Katana Letter Opener", description: "Hand-forged steel letter opener with hamon line.", price: 49.99, priceText: "$49.99", dataPrice: "49.99" },
  { id: 2, name: "Zen Garden Starter Kit", description: "Miniature raked sand garden with stone set.", price: 29.5, priceText: "$29.50", dataPrice: "29.5" },
  { id: 3, name: "Ronin Tea Set", description: "Cast iron teapot with two cups, matte black finish.", price: 74.0, priceText: "$74.00", dataPrice: "74.0" },
  { id: 4, name: "Bamboo Bento Box", description: "Two-tier lacquered bento with cloth wrap.", price: 38.25, priceText: "$38.25", dataPrice: "38.25" },
  { id: 5, name: "Calligraphy Brush Set", description: "Five brushes of varying weight with ink stone.", price: 42.0, priceText: "$42.00", dataPrice: "42.0" },
  { id: 6, name: "Origami Paper Pack", description: "200 sheets of washi paper in twelve colors.", price: 15.75, priceText: "$15.75", dataPrice: "15.75" },
  { id: 7, name: "Incense Sampler", description: "Twelve sticks of cedar, sandalwood and hinoki.", price: 22.0, priceText: "$22.00", dataPrice: "22.0" },
  { id: 8, name: "Lucky Cat Figurine", description: "Ceramic maneki-neko, left paw raised.", price: 19.99, priceText: "$19.99", dataPrice: "19.99" },
];
