import Ember from 'ember';

export default Ember.Object.extend({
  fixCalc: null,
  flightMap: null,

  map: Ember.computed.readOnly('flightMap.map'),
  flights: Ember.computed.readOnly('fixCalc.flights'),

  hover_disabled: Ember.computed.or('fixCalc.isRunning', 'flightMap.cesiumEnabled'),
  hover_enabled: Ember.computed.not('hover_disabled'),

  init() {
    this._super(...arguments);

    let map = this.get('map');

    map.on('pointermove', e => {
      if (!this.get('hover_enabled') || e.dragging)
        return;

      let coordinate = map.getEventCoordinate(e.originalEvent);
      this.displaySnap(coordinate);
    });
  },

  displaySnap(coordinate) {
    let map = this.get('map');

    let flight_path_source = this.get('flights.source');

    let closest_feature = flight_path_source
        .getClosestFeatureToCoordinate(coordinate);

    if (closest_feature !== null) {
      let geometry = closest_feature.getGeometry();
      let closest_point = geometry.getClosestPoint(coordinate);

      let feature_pixel = map.getPixelFromCoordinate(closest_point);
      let mouse_pixel = map.getPixelFromCoordinate(coordinate);

      let squared_distance = Math.pow(mouse_pixel[0] - feature_pixel[0], 2) +
                             Math.pow(mouse_pixel[1] - feature_pixel[1], 2);

      // Set the time when the mouse hovers the map
      if (squared_distance > 100) {
        this.get('fixCalc').resetTime();
      } else {
        this.get('fixCalc').set('time', closest_point[3]);
      }
    }

    map.render();
  },
});
