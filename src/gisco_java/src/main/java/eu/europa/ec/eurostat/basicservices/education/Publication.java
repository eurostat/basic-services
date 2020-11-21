/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.education;

import eu.europa.ec.eurostat.basicservices.BasicServicePublication;

/**
 * Publication script for education.
 * 
 * @author julien Gaffuri
 *
 */
public class Publication {

	static String destinationBasePath = "E:/users/gaffuju/eclipse_workspace/basic-services/";
	//static String destinationBasePath = "E:/users/clemoki/workspace/basic-services/";

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		BasicServicePublication.publish("education", EducationUtil.path, destinationBasePath, EducationUtil.ccs, EducationUtil.cols_, EducationUtil.ats);
	}

}
