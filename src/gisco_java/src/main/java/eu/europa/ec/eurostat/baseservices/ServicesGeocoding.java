/**
 * 
 */
package eu.europa.ec.eurostat.baseservices;

import java.util.Collection;
import java.util.Map;

import eu.europa.ec.eurostat.jgiscotools.deprecated.NUTSUtils;
import eu.europa.ec.eurostat.jgiscotools.geocoding.base.Geocoder;
import eu.europa.ec.eurostat.jgiscotools.geocoding.base.GeocodingAddress;
import eu.europa.ec.eurostat.jgiscotools.geocoding.base.GeocodingResult;

/**
 * @author julien Gaffuri
 *
 */
public class ServicesGeocoding {

	public static GeocodingAddress toGeocodingAddress(Map<String,String> s, boolean usePostcode) {
		return new GeocodingAddress(
				null,
				s.get("house_number"),
				s.get("street"),
				s.get("city"),
				s.get("cc"),
				getCountryName(s.get("cc")),
				usePostcode? s.get("postcode") : null
				);
	}

	public static GeocodingResult get(Geocoder gc, Map<String,String> s, boolean usePostcode, boolean print) {
		return gc.geocode(toGeocodingAddress(s, usePostcode), print);
	}

	public static void set(Map<String,String> s, GeocodingResult gr, String lonCol, String latCol) {
		s.put(latCol, "" + gr.position.y);
		s.put(lonCol, "" + gr.position.x);
		//s.put("geo_matching", "" + gr.matching);
		//s.put("geo_confidence", "" + gr.confidence);
		s.put("geo_qual", "" + gr.quality);		
	}

	public static void set(Map<String,String> s, Geocoder gc, String lonCol, String latCol, boolean usePostcode, boolean print) {
		GeocodingResult gr = get(gc, s, usePostcode, print);
		if(print) System.out.println(gr.position  + "  --- " + gr.quality + " --- " + gr.matching + " --- " + gr.confidence);
		set(s, gr, lonCol, latCol);
	}

	public static void set(Geocoder gc, Collection<Map<String,String>> services, String lonCol, String latCol, boolean usePostcode, boolean print) {
		int fails = 0;
		for(Map<String,String> s : services) {
			GeocodingResult gr = get(gc, s, usePostcode, print);
			if(print) System.out.println(gr.position  + "  --- " + gr.quality + " --- " + gr.matching + " --- " + gr.confidence);
			if(gr.position.getX()==0 && gr.position.getY()==0) fails++;
			set(s, gr, lonCol, latCol);
		}
		System.out.println("Failures: " + fails + "/" + services.size());
	}




	public static void improve(Geocoder gc, Map<String, String> s, boolean usePostcode, boolean print) {

		//check if position is not already perfect
		int geoqIni = Integer.parseInt(s.get("geo_qual"));
		if(geoqIni == 1 || geoqIni == -1) {
			//if(print) System.out.println("Position already OK for " + s.get("id"));
			return;
		}

		//find new candidate position
		GeocodingResult gr = get(gc, s, usePostcode, print);
		if(gr.quality >= geoqIni) {
			if(print) System.out.println("No positionning improvement for " + s.get("id"));
			return;
		}

		if(print) System.out.println("Positionning improvement for " + s.get("id") + ". "+ geoqIni + " -> " + gr.quality);
		ServicesGeocoding.set(s, gr, "lon", "lat");
	}

	public static String getCountryName(String cc) {
		switch (cc) {
		case "GP": return "Guadeloupe";
		case "MQ": return "Martinique";
		case "GF": return "Guyane française";
		case "RE": return "Réunion";
		case "PM": return "Saint-Pierre et Miquelon";
		case "YT": return "Mayotte";
		}
		String name = NUTSUtils.getName(cc);
		name = name.replace(" (until 1990 former territory of the FRG)", "");
		return name;
	}

}
