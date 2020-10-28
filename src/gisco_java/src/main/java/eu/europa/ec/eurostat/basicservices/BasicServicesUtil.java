/**
 * 
 */
package eu.europa.ec.eurostat.basicservices;

import java.text.SimpleDateFormat;
import java.util.Collection;

import eu.europa.ec.eurostat.jgiscotools.feature.Feature;

/**
 * @author gaffuju
 *
 */
public class BasicServicesUtil {

	//path to the shared-data folder
	public static String path = "E:/dissemination/shared-data/MS_data/";

	//date format
	public static SimpleDateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy");

	/**
	 * Ensure some feature attributes have an Integer type.
	 * 
	 * @param fs
	 * @param atts
	 */
	public static void setAttributeTypeAsIntegerTypes(Collection<Feature> fs, String... atts) {
		for(Feature f : fs) {
			for(String att : atts) {
				var v = f.getAttribute(att);
				if(v==null) continue;
				if("".equals(v)) f.setAttribute(att, null);
				else f.setAttribute(att, Integer.parseInt(v.toString()));
			}
		}
	}

	/**
	 * Ensure some feature attributes have an Double type.
	 * 
	 * @param fs
	 * @param atts
	 */
	public static void setAttributeTypeAsDoubleTypes(Collection<Feature> fs, String... atts) {
		for(Feature f : fs) {
			for(String att : atts) {
				var v = f.getAttribute(att);
				if(v==null) continue;
				if("".equals(v)) f.setAttribute(att, null);
				else f.setAttribute(att, Double.parseDouble(v.toString()));
			}
		}
	}

}
