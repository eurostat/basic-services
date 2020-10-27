/**
 * 
 */
package eu.europa.ec.eurostat.basicservices;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Map;

import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.LineString;

import eu.europa.ec.eurostat.jgiscotools.feature.Feature;
import eu.europa.ec.eurostat.jgiscotools.geocoding.BingGeocoder;
import eu.europa.ec.eurostat.jgiscotools.geocoding.GISCOGeocoderAPI;
import eu.europa.ec.eurostat.jgiscotools.geocoding.GISCOGeocoderNominatimDetail;
import eu.europa.ec.eurostat.jgiscotools.geocoding.GISCOGeocoderNominatimQuery;
import eu.europa.ec.eurostat.jgiscotools.geocoding.base.Geocoder;
import eu.europa.ec.eurostat.jgiscotools.geocoding.base.GeocodingAddress;
import eu.europa.ec.eurostat.jgiscotools.geocoding.base.GeocodingResult;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.CRSUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.GeoData;
import eu.europa.ec.eurostat.jgiscotools.util.GeoDistanceUtil;

public class GeocodingTest {

	public static void main(String[] args) {
		System.out.println("Start");

		String inPath = "C:\\Users\\gaffuju\\workspace\\healthcare-services\\data\\";
		String outPath = "C:\\Users\\gaffuju\\Desktop/gv/";

		//load hospital addresses - the ones with geolocation and address
		for(String cc : new String[] {"PT", "CH", "BE", "NL", "DE", "DK"}) {
			System.out.println("*** " + cc);
			ArrayList<Map<String, String>> data = CSVUtil.load(inPath + "csv/"+cc+".csv");
			System.out.println(data.size());

			LocalParameters.loadProxySettings();
			Collection<Feature> outB = validate(data, BingGeocoder.get(), "lon", "lat");
			System.out.println("Save - " + outB.size());
			GeoData.save(outB, outPath + "geocoderValidationBing_"+cc+".gpkg", CRSUtil.getWGS_84_CRS());

			Collection<Feature> outGAPI = validate(data, GISCOGeocoderAPI.get(), "lon", "lat");
			System.out.println("Save - " + outGAPI.size());
			GeoData.save(outGAPI, outPath + "geocoderValidationGISCO_API_"+cc+".gpkg", CRSUtil.getWGS_84_CRS());

			Collection<Feature> outGQ = validate(data, GISCOGeocoderNominatimQuery.get(), "lon", "lat");
			System.out.println("Save - " + outGQ.size());
			GeoData.save(outGQ, outPath + "geocoderValidationGISCO_NominatimQuery_"+cc+".gpkg", CRSUtil.getWGS_84_CRS());

			Collection<Feature> outGD = validate(data, GISCOGeocoderNominatimDetail.get(), "lon", "lat");
			System.out.println("Save - " + outGD.size());
			GeoData.save(outGD, outPath + "geocoderValidationGISCO_NominatimDetail_"+cc+".gpkg", CRSUtil.getWGS_84_CRS());
		}

		System.out.println("End");
	}


	public static Collection<Feature> validate(Collection<Map<String, String>> data, Geocoder gc, String lonCol, String latCol) {
		ArrayList<Feature> out = new ArrayList<>();
		GeometryFactory gf = new GeometryFactory();
		for(Map<String, String> d : data) {

			//get position
			Coordinate c = new Coordinate(Double.parseDouble(d.get(lonCol)), Double.parseDouble(d.get(latCol)));

			//get address
			GeocodingAddress add = ServicesGeocoding.toGeocodingAddress(d, true);

			//get geocoder position 
			GeocodingResult gr = gc.geocode(add, true);
			System.out.println(gr.position);

			//build output feature
			Feature f = new Feature();
			LineString ls = gf.createLineString(new Coordinate[] { c, gr.position });
			f.setGeometry(ls);
			double dist = 1000 * GeoDistanceUtil.getDistanceKM(gr.position.x, gr.position.y, c.x, c.y);
			f.setAttribute("dist", dist);
			f.setAttribute("qual", gr.quality);

			f.getAttributes().putAll(d);

			out.add(f);
		}
		return out;
	}

}
