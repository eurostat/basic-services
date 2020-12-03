/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.education;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Map;

import eu.europa.ec.eurostat.basicservices.BasicServicesValidation;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;

/**
 * Check if the education CSV files are compliant with the specs.
 * 
 * @author julien Gaffuri
 *
 */
public class Validation {

	/**
	 * run validation process for each country
	 * @param args 
	 */
	public static void main(String[] args) {
		System.out.println("Start");
		for(String cc : EducationUtil.ccs) {
			System.out.println("*** " + cc);
			ArrayList<Map<String, String>> data = CSVUtil.load(EducationUtil.path + cc+"/"+cc+".csv");
			System.out.println(data.size());
			validate(true, data, cc);
		}
		System.out.println("End");
	}

	/**
	 * Validate data for a specific country.
	 * 
	 * @param data
	 * @param cc
	 */
	public static void validate(boolean showErrorMessage, Collection<Map<String, String>> data, String cc) {
		boolean b;

		//validation on all aspects common to other basic services
		BasicServicesValidation.validate(showErrorMessage, data, cc, EducationUtil.cols_);

		//TODO other tests ?
		//check empty columns

		//check fields - 0/1/2/3/4/5/6/7/8
		b = BasicServicesValidation.checkValuesAmongWithDelim(showErrorMessage, data, "fields", "-", "", "0", "1", "2", "3", "4", "5", "6", "7", "8");
		if(!b) System.err.println("Problem with fields values for " + cc);		

		//check levels - 0/1/2/3
		b = BasicServicesValidation.checkValuesAmongWithDelim(showErrorMessage, data, "levels", "-", "", "0", "1", "2", "3");
		if(!b) System.err.println("Problem with levels values for " + cc);

		//check public_private - public/private
		b = BasicServicesValidation.checkValuesAmong(showErrorMessage, data, "public_private", "", "public", "private");
		if(!b) System.err.println("Problem with public_private values for " + cc);

		//non null columns
		b = BasicServicesValidation.checkValuesNotNullOrEmpty(data, "name");
		if(!b) System.err.println("Missing name values for " + cc);

		//check int values
		BasicServicesValidation.checkIntValues(showErrorMessage, data, "max_students");
		if(!b) System.err.println("Problem (non integer values) for max_students values for " + cc);
		BasicServicesValidation.checkIntValues(showErrorMessage, data, "enrollment");
		if(!b) System.err.println("Problem (non integer values) for enrollment values for " + cc);

	}

}
